import os
import time
import random
import argparse
import json
import numpy as np
import pandas as pd

from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity

# Import your project code (loads artifacts)
import local_recommender as lr


def make_abstract_snippet_query(summary: str, min_words=35, max_words=60) -> str:
    """
    Neutral query: take a snippet from the abstract, not the title.
    This reduces exact-match bias toward TF-IDF.
    """
    if not isinstance(summary, str):
        return ""
    s = " ".join(summary.strip().split())
    if not s:
        return ""
    words = s.split()
    if len(words) <= min_words:
        return s

    # Take a mid-portion snippet to avoid always grabbing the opening boilerplate sentence
    start_max = max(1, len(words) - max_words)
    start = min(len(words) // 4, start_max)
    length = random.randint(min_words, min(max_words, len(words) - start))
    return " ".join(words[start:start + length])


def retrieve_tfidf(query: str, top_k: int):
    q = lr.tfidf_vectorizer.transform([lr.clean_text(query)])
    scores = cosine_similarity(q, lr.tfidf_matrix)[0]
    idx = np.argsort(scores)[::-1][:top_k]
    return idx.tolist(), scores[idx].tolist()


def retrieve_semantic_fullscan(query: str, top_k: int):
    q_emb = normalize(lr.sbert_model.encode([lr.light_clean(query)], convert_to_numpy=True))
    scores = cosine_similarity(q_emb, lr.sbert_embeddings)[0]
    idx = np.argsort(scores)[::-1][:top_k]
    return idx.tolist(), scores[idx].tolist()


def retrieve_hybrid_clustered(query: str, top_k: int):
    res = lr.recommend_local(query, top_k=top_k)
    # recommend_local returns titles; map titles back to indices (best-effort)
    titles = [x["title"] for x in res["results"]]
    # Use first match for each title (should be unique in most cases)
    idxs = []
    for t in titles:
        matches = lr.df.index[lr.df["titles"] == t].tolist()
        if matches:
            idxs.append(matches[0])
    scores = [x.get("relevance_score") for x in res["results"]]
    return idxs, scores


def load_queries_from_file(queries_file: str):
    with open(queries_file, "r", encoding="utf-8") as f:
        payload = json.load(f)

    queries = []
    for i, item in enumerate(payload):
        if isinstance(item, str):
            query_text = item.strip()
        else:
            query_text = str(item.get("query", "")).strip()

        if not query_text:
            continue

        queries.append({
            "query_id": i,
            "query_source_doc_index": "",
            "query_source_title": "",
            "query_text": query_text,
        })

    return queries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n_queries", type=int, default=30, help="How many queries to sample")
    ap.add_argument("--top_k", type=int, default=10, help="How many results per system per query")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=str, default="judgments.csv")
    ap.add_argument("--queries-file", type=str, default="", help="Optional JSON file of fixed custom queries")
    args = ap.parse_args()

    random.seed(args.seed)
    np.random.seed(args.seed)

    print("Initializing local recommender (loads artifacts)...")
    lr.init_local_recommender()

    df = lr.df
    n = len(df)
    if n == 0:
        raise RuntimeError("Dataset is empty.")

    query_specs = []
    if args.queries_file:
        query_specs = load_queries_from_file(args.queries_file)
        if not query_specs:
            raise RuntimeError("No valid queries found in queries file.")
    else:
        candidate_idxs = list(range(n))
        random.shuffle(candidate_idxs)
        query_doc_idxs = candidate_idxs[: args.n_queries]

        for qid, doc_idx in enumerate(query_doc_idxs):
            title = str(df.loc[doc_idx, "titles"])
            abstract = str(df.loc[doc_idx, "summaries"])

            query_text = make_abstract_snippet_query(abstract)
            if not query_text:
                query_text = title

            query_specs.append({
                "query_id": qid,
                "query_source_doc_index": int(doc_idx),
                "query_source_title": title,
                "query_text": query_text,
            })

    rows = []

    for spec in query_specs:
        qid = spec["query_id"]
        doc_idx = spec["query_source_doc_index"]
        title = spec["query_source_title"]
        query_text = spec["query_text"]

        # --- TF-IDF baseline ---
        t0 = time.perf_counter()
        tfidf_idxs, tfidf_scores = retrieve_tfidf(query_text, args.top_k)
        tfidf_ms = (time.perf_counter() - t0) * 1000.0

        for rank, (rid, score) in enumerate(zip(tfidf_idxs, tfidf_scores), start=1):
            rows.append({
                "query_id": qid,
                "query_source_doc_index": doc_idx,
                "query_source_title": title,
                "query_text": query_text,
                "system": "tfidf_fullscan",
                "rank": rank,
                "result_doc_index": int(rid),
                "result_title": str(df.loc[rid, "titles"]),
                "result_abstract": str(df.loc[rid, "summaries"]),
                "score": float(score),
                "latency_ms": float(tfidf_ms),
                "label": ""  # you fill 1/0
            })

        # --- Semantic-only baseline (full scan) ---
        t0 = time.perf_counter()
        sem_idxs, sem_scores = retrieve_semantic_fullscan(query_text, args.top_k)
        sem_ms = (time.perf_counter() - t0) * 1000.0

        for rank, (rid, score) in enumerate(zip(sem_idxs, sem_scores), start=1):
            rows.append({
                "query_id": qid,
                "query_source_doc_index": doc_idx,
                "query_source_title": title,
                "query_text": query_text,
                "system": "semantic_fullscan",
                "rank": rank,
                "result_doc_index": int(rid),
                "result_title": str(df.loc[rid, "titles"]),
                "result_abstract": str(df.loc[rid, "summaries"]),
                "score": float(score),
                "latency_ms": float(sem_ms),
                "label": ""
            })

        # --- Proposed system (clustered FAISS + hybrid rerank) ---
        t0 = time.perf_counter()
        hyb_idxs, hyb_scores = retrieve_hybrid_clustered(query_text, args.top_k)
        hyb_ms = (time.perf_counter() - t0) * 1000.0

        for rank, rid in enumerate(hyb_idxs, start=1):
            score = hyb_scores[rank - 1] if hyb_scores and (rank - 1) < len(hyb_scores) else None
            rows.append({
                "query_id": qid,
                "query_source_doc_index": doc_idx,
                "query_source_title": title,
                "query_text": query_text,
                "system": "hybrid_clustered_faiss",
                "rank": rank,
                "result_doc_index": int(rid),
                "result_title": str(df.loc[rid, "titles"]),
                "result_abstract": str(df.loc[rid, "summaries"]),
                "score": float(score) if score is not None else "",
                "latency_ms": float(hyb_ms),
                "label": ""
            })

        print(f"Done query {qid+1}/{len(query_specs)}")

    out_path = os.path.join(os.getcwd(), args.out)
    out_df = pd.DataFrame(rows)

    # Helpful sorting for annotation
    out_df = out_df.sort_values(["query_id", "system", "rank"]).reset_index(drop=True)
    out_df.to_csv(out_path, index=False)
    print(f"\nWrote: {out_path}")
    print("Next: open this CSV and fill the 'label' column with 1 (relevant) or 0 (not relevant).")


if __name__ == "__main__":
    main()