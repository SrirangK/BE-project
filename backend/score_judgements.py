import argparse
import numpy as np
import pandas as pd


def dcg_at_k(labels):
    # labels: list of 0/1 in ranked order
    dcg = 0.0
    for i, rel in enumerate(labels, start=1):
        dcg += (2**rel - 1) / np.log2(i + 1)
    return dcg


def ndcg_at_k(labels):
    actual = dcg_at_k(labels)
    ideal = dcg_at_k(sorted(labels, reverse=True))
    if ideal == 0:
        return 0.0
    return actual / ideal


def mrr_at_k(labels):
    for i, rel in enumerate(labels, start=1):
        if rel == 1:
            return 1.0 / i
    return 0.0


def precision_at_k(labels):
    if not labels:
        return 0.0
    return float(np.mean(labels))


def recall_at_k(labels, total_relevant):
    if total_relevant <= 0:
        return 0.0
    return float(np.sum(labels) / total_relevant)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=str, default="judgments.csv")
    ap.add_argument("--k", type=int, default=10)
    args = ap.parse_args()

    df = pd.read_csv(args.csv)

    # Basic validation
    if "label" not in df.columns:
        raise RuntimeError("CSV missing 'label' column.")
    if df["label"].isna().any():
        # allow blanks, but they must be filled before scoring
        pass

    # Convert labels
    def parse_label(x):
        if pd.isna(x):
            return None
        s = str(x).strip()
        if s == "":
            return None
        if s not in ("0", "1"):
            return None
        return int(s)

    df["label_parsed"] = df["label"].apply(parse_label)
    missing = df["label_parsed"].isna().sum()
    if missing > 0:
        raise RuntimeError(f"You still have {missing} unlabeled rows. Fill them with 0/1 before scoring.")

    k = args.k
    systems = sorted(df["system"].unique().tolist())

    pooled_relevant_per_query = (
        df.groupby(["query_id", "result_doc_index"], as_index=False)["label_parsed"]
        .max()
        .groupby("query_id")["label_parsed"]
        .sum()
        .to_dict()
    )

    results = []

    for system in systems:
        sys_df = df[df["system"] == system].copy()

        # group by query_id, sort by rank, take top-k
        per_query = []
        for qid, g in sys_df.groupby("query_id"):
            g = g.sort_values("rank").head(k)
            labels = g["label_parsed"].tolist()
            padded_labels = labels + [0] * max(0, k - len(labels))
            total_relevant = int(pooled_relevant_per_query.get(qid, 0))

            per_query.append({
                "ndcg": ndcg_at_k(padded_labels),
                "mrr": mrr_at_k(padded_labels),
                "p_at_k": precision_at_k(padded_labels),
                "recall_at_k": recall_at_k(labels, total_relevant),
                "latency_ms": float(g["latency_ms"].iloc[0]) if "latency_ms" in g.columns and len(g) else np.nan
            })

        ndcg = float(np.mean([x["ndcg"] for x in per_query]))
        mrr = float(np.mean([x["mrr"] for x in per_query]))
        p_at_k = float(np.mean([x["p_at_k"] for x in per_query]))
        recall = float(np.mean([x["recall_at_k"] for x in per_query]))
        lat = float(np.mean([x["latency_ms"] for x in per_query]))

        results.append({
            "system": system,
            f"Precision@{k}": round(p_at_k, 4),
            f"Recall@{k}": round(recall, 4),
            f"MRR@{k}": round(mrr, 4),
            f"nDCG@{k}": round(ndcg, 4),
            "AvgLatencyMs": round(lat, 2),
            "n_queries": len(per_query)
        })

    out = pd.DataFrame(results).sort_values("system")
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()