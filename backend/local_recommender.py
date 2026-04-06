import os
import pickle
import numpy as np
import pandas as pd
import faiss
import re

from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

ART_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

ALPHA = 0.70
BETA = 0.30

df = None
tfidf_vectorizer = None
tfidf_matrix = None
sbert_model = None
sbert_embeddings = None
kmeans = None
cluster_mappings = None

def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return text

def light_clean(text):
    return re.sub(r"\s+", " ", text).strip()

def init_local_recommender():
    global df, tfidf_vectorizer, tfidf_matrix, sbert_model, sbert_embeddings, kmeans, cluster_mappings

    df = pd.read_csv(os.path.join(ART_DIR, "arxiv_cleaned.csv"))
    with open(os.path.join(ART_DIR, "tfidf_vectorizer.pkl"), "rb") as f:
        tfidf_vectorizer = pickle.load(f)

    # rebuild tfidf matrix from stored text column
    tfidf_matrix = tfidf_vectorizer.transform(df["text_tfidf"].fillna("").tolist())

    sbert_embeddings = np.load(os.path.join(ART_DIR, "sbert_embeddings.npy"))
    sbert_embeddings = normalize(sbert_embeddings)

    with open(os.path.join(ART_DIR, "kmeans_model.pkl"), "rb") as f:
        kmeans = pickle.load(f)

    with open(os.path.join(ART_DIR, "cluster_mappings.pkl"), "rb") as f:
        cluster_mappings = pickle.load(f)

    sbert_model = SentenceTransformer("sentence-transformers/allenai-specter")

def recommend_local(query: str, top_k=5, n_probe_clusters=3):
    q_tfidf = tfidf_vectorizer.transform([clean_text(query)])
    q_sbert = normalize(sbert_model.encode([light_clean(query)], convert_to_numpy=True))

    cluster_centers = normalize(kmeans.cluster_centers_)
    sims = cosine_similarity(q_sbert, cluster_centers)[0]
    top_clusters = sims.argsort()[::-1][:n_probe_clusters]

    all_retrieved = []
    for cid in top_clusters:
        idx_path = os.path.join(ART_DIR, "faiss_clusters", f"cluster_{cid}.index")
        index = faiss.read_index(idx_path)
        D, I = index.search(q_sbert.astype("float32"), top_k * 5)

        original_indices = cluster_mappings[cid]
        for i in I[0]:
            if i >= 0:
                all_retrieved.append(original_indices[i])

    all_retrieved = list(set(all_retrieved))
    if not all_retrieved:
        return {"cluster_id": int(top_clusters[0]), "cluster_keywords": [], "results": []}

    s_scores = cosine_similarity(q_sbert, sbert_embeddings[all_retrieved])[0]
    t_scores = cosine_similarity(q_tfidf, tfidf_matrix[all_retrieved])[0]
    final_scores = ALPHA * s_scores + BETA * t_scores

    ranked = sorted(zip(all_retrieved, final_scores), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for doc_id, score in ranked:
        results.append({
            "source": "local",
            "paper_id": None,
            "title": str(df.loc[doc_id, "titles"]),
            "year": None,
            "abstract": str(df.loc[doc_id, "summaries"]) if "summaries" in df.columns else None,
            "url": None,
            "open_access_pdf": None,
            "citations": None,
            "relevance_score": float(round(score, 4)),
            "author_h_index": None
        })

    return {
        "cluster_id": int(top_clusters[0]),
        "cluster_keywords": [],
        "results": results
    }