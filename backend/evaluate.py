import argparse
import json
import random
import time

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

import local_recommender
from local_recommender import clean_text, init_local_recommender, recommend_local


def reciprocal_rank(relevant_set, retrieved_indices):
    for i, idx in enumerate(retrieved_indices):
        if idx in relevant_set:
            return 1.0 / (i + 1)
    return 0.0


def hit_rate_at_k(relevant_set, retrieved_indices):
    return 1.0 if any(idx in relevant_set for idx in retrieved_indices) else 0.0


def recall_at_k(relevant_set, retrieved_indices):
    if not relevant_set:
        return 0.0
    hits = sum(1 for idx in retrieved_indices if idx in relevant_set)
    return hits / len(relevant_set)


def precision_at_k(relevant_set, retrieved_indices):
    if not retrieved_indices:
        return 0.0
    hits = sum(1 for idx in retrieved_indices if idx in relevant_set)
    return hits / len(retrieved_indices)


def ndcg_at_k(relevant_set, retrieved_indices):
    if not relevant_set:
        return 0.0

    dcg = 0.0
    for rank, idx in enumerate(retrieved_indices, start=1):
        if idx in relevant_set:
            dcg += 1.0 / np.log2(rank + 1)

    ideal_hits = min(len(relevant_set), len(retrieved_indices))
    if ideal_hits == 0:
        return 0.0

    idcg = sum(1.0 / np.log2(rank + 1) for rank in range(1, ideal_hits + 1))
    return dcg / idcg


def get_hybrid_ranked_indices(query, top_k, n_probe_clusters=3):
    df = local_recommender.df
    res = recommend_local(query, top_k=top_k, n_probe_clusters=n_probe_clusters)
    retrieved_titles = [r["title"] for r in res.get("results", [])]

    ranked_indices = []
    seen = set()
    for title in retrieved_titles:
        matches = df[df["titles"] == title].index.tolist()
        if matches:
            idx = int(matches[0])
            if idx not in seen:
                ranked_indices.append(idx)
                seen.add(idx)

    return ranked_indices


def get_tfidf_ranked_indices(query, top_k):
    q_tfidf = local_recommender.tfidf_vectorizer.transform([clean_text(query)])
    t_scores = cosine_similarity(q_tfidf, local_recommender.tfidf_matrix)[0]
    return t_scores.argsort()[::-1][:top_k].tolist()


def init_metric_store():
    return {
        "latency_ms": [],
        "mrr": [],
        "hit_rate": [],
        "recall": [],
        "precision": [],
        "ndcg": [],
    }


def update_metrics(metrics, relevant_set, ranked_indices, latency_ms):
    metrics["latency_ms"].append(latency_ms)
    metrics["mrr"].append(reciprocal_rank(relevant_set, ranked_indices))
    metrics["hit_rate"].append(hit_rate_at_k(relevant_set, ranked_indices))
    metrics["recall"].append(recall_at_k(relevant_set, ranked_indices))
    metrics["precision"].append(precision_at_k(relevant_set, ranked_indices))
    metrics["ndcg"].append(ndcg_at_k(relevant_set, ranked_indices))


def print_metric_block(name, metrics, top_k):
    print(f"{name}:")
    print(f"  Avg Latency:    {np.mean(metrics['latency_ms']):.2f} ms")
    print(f"  MRR@{top_k}:        {np.mean(metrics['mrr']):.4f}")
    print(f"  HitRate@{top_k}:    {np.mean(metrics['hit_rate']):.4f}")
    print(f"  Recall@{top_k}:     {np.mean(metrics['recall']):.4f}")
    print(f"  Precision@{top_k}:  {np.mean(metrics['precision']):.4f}")
    print(f"  NDCG@{top_k}:       {np.mean(metrics['ndcg']):.4f}")


def evaluate_self_retrieval(sample_size=50, top_k=10, seed=42, n_probe_clusters=3):
    print("Initializing Recommender...")
    init_local_recommender()
    df = local_recommender.df

    if sample_size > len(df):
        sample_size = len(df)

    random.seed(seed)
    test_indices = random.sample(range(len(df)), sample_size)

    hybrid = init_metric_store()
    tfidf = init_metric_store()

    print("Running self-retrieval evaluation...")
    for idx in test_indices:
        query = str(df.loc[idx, "titles"])
        relevant_set = {idx}

        start_time = time.time()
        hybrid_ranked = get_hybrid_ranked_indices(query, top_k, n_probe_clusters=n_probe_clusters)
        hybrid_time = (time.time() - start_time) * 1000
        update_metrics(hybrid, relevant_set, hybrid_ranked, hybrid_time)

        start_time = time.time()
        tfidf_ranked = get_tfidf_ranked_indices(query, top_k)
        tfidf_time = (time.time() - start_time) * 1000
        update_metrics(tfidf, relevant_set, tfidf_ranked, tfidf_time)

    print("\n=== SELF-RETRIEVAL RESULTS ===")
    print_metric_block("Hybrid System (Proposed)", hybrid, top_k)
    print()
    print_metric_block("Baseline (Pure TF-IDF)", tfidf, top_k)


def resolve_relevant_indices(query_row):
    df = local_recommender.df
    relevant_indices = set()

    for idx in query_row.get("relevant_indices", []):
        if isinstance(idx, int) and 0 <= idx < len(df):
            relevant_indices.add(idx)

    for title in query_row.get("relevant_titles", []):
        matches = df[df["titles"] == title].index.tolist()
        if matches:
            relevant_indices.add(int(matches[0]))

    return relevant_indices


def evaluate_custom_queries(queries_file, top_k=10, n_probe_clusters=3):
    print("Initializing Recommender...")
    init_local_recommender()

    with open(queries_file, "r", encoding="utf-8") as f:
        query_rows = json.load(f)

    hybrid = init_metric_store()
    tfidf = init_metric_store()
    valid_queries = 0
    skipped_queries = 0

    print(f"Running custom-query evaluation from: {queries_file}")
    for row in query_rows:
        query = str(row.get("query", "")).strip()
        if not query:
            skipped_queries += 1
            continue

        relevant_set = resolve_relevant_indices(row)
        if not relevant_set:
            skipped_queries += 1
            continue

        valid_queries += 1

        start_time = time.time()
        hybrid_ranked = get_hybrid_ranked_indices(query, top_k, n_probe_clusters=n_probe_clusters)
        hybrid_time = (time.time() - start_time) * 1000
        update_metrics(hybrid, relevant_set, hybrid_ranked, hybrid_time)

        start_time = time.time()
        tfidf_ranked = get_tfidf_ranked_indices(query, top_k)
        tfidf_time = (time.time() - start_time) * 1000
        update_metrics(tfidf, relevant_set, tfidf_ranked, tfidf_time)

    if valid_queries == 0:
        print("No valid custom queries with relevance labels found.")
        print("Each query item must include at least one relevant title or index.")
        return

    print("\n=== CUSTOM QUERY RESULTS ===")
    print(f"Valid Queries:   {valid_queries}")
    print(f"Skipped Queries: {skipped_queries}")
    print_metric_block("Hybrid System (Proposed)", hybrid, top_k)
    print()
    print_metric_block("Baseline (Pure TF-IDF)", tfidf, top_k)


def parse_args():
    parser = argparse.ArgumentParser(description="Evaluate local recommender")
    parser.add_argument(
        "--mode",
        choices=["self", "custom"],
        default="self",
        help="self: title self-retrieval; custom: evaluate manually labeled semantic queries",
    )
    parser.add_argument("--top-k", type=int, default=10, help="Top-k cutoff")
    parser.add_argument("--sample-size", type=int, default=50, help="Samples for self mode")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for self mode")
    parser.add_argument("--n-probe-clusters", type=int, default=3, help="Clusters probed by hybrid")
    parser.add_argument(
        "--queries-file",
        type=str,
        default="artifacts/custom_queries_example.json",
        help="JSON file for custom mode",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.mode == "self":
        evaluate_self_retrieval(
            sample_size=args.sample_size,
            top_k=args.top_k,
            seed=args.seed,
            n_probe_clusters=args.n_probe_clusters,
        )
    else:
        evaluate_custom_queries(
            queries_file=args.queries_file,
            top_k=args.top_k,
            n_probe_clusters=args.n_probe_clusters,
        )
