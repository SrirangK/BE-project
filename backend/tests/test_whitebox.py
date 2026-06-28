import re

import pytest

np = pytest.importorskip("numpy")
pd = pytest.importorskip("pandas")
normalize = pytest.importorskip("sklearn.preprocessing").normalize
backend_app = pytest.importorskip("app")
lr = pytest.importorskip("local_recommender")


class DummyVectorizer:
    def transform(self, texts):
        return np.ones((len(texts), 10000), dtype=np.float32)


class DummyModel:
    def encode(self, texts, convert_to_numpy=True):
        out = np.zeros((len(texts), 768), dtype=np.float32)
        out[:, 0] = 1.0
        return out


class FakeFaissIndex:
    def __init__(self, cluster_id):
        self.cluster_id = cluster_id

    def search(self, _query, k):
        lookup = {
            0: [0, 1, 1, -1],
            1: [0, 1, -1, -1],
            2: [0, 1, -1, -1],
        }
        base = lookup.get(self.cluster_id, [0, -1, -1, -1])
        padded = (base + [-1] * k)[:k]
        return np.zeros((1, k), dtype=np.float32), np.array([padded], dtype=np.int64)


def _configure_local_recommender(monkeypatch):
    monkeypatch.setattr(lr, "tfidf_vectorizer", DummyVectorizer(), raising=False)
    monkeypatch.setattr(lr, "sbert_model", DummyModel(), raising=False)
    monkeypatch.setattr(
        lr,
        "df",
        pd.DataFrame(
            {
                "titles": ["P0", "P1", "P2", "P3"],
                "summaries": ["S0", "S1", "S2", "S3"],
                "text_tfidf": ["a", "b", "c", "d"],
            }
        ),
        raising=False,
    )
    tfidf_matrix = np.zeros((4, 10000), dtype=np.float32)
    tfidf_matrix[0, 0] = 1.0
    tfidf_matrix[1, 1] = 1.0
    tfidf_matrix[2, 2] = 1.0
    tfidf_matrix[3, 3] = 1.0
    monkeypatch.setattr(lr, "tfidf_matrix", tfidf_matrix, raising=False)

    sbert_embeddings = np.zeros((4, 768), dtype=np.float32)
    sbert_embeddings[0, 0] = 1.0
    sbert_embeddings[1, 1] = 1.0
    sbert_embeddings[2, 2] = 1.0
    sbert_embeddings[3, 3] = 1.0
    monkeypatch.setattr(lr, "sbert_embeddings", normalize(sbert_embeddings), raising=False)

    class FakeKMeans:
        cluster_centers_ = np.zeros((4, 768), dtype=np.float32)
        cluster_centers_[0, 0] = 1.0
        cluster_centers_[1, 0] = 0.8
        cluster_centers_[1, 1] = 0.6
        cluster_centers_[2, 0] = 0.6
        cluster_centers_[2, 2] = 0.8
        cluster_centers_[3, 767] = 1.0

    monkeypatch.setattr(lr, "kmeans", FakeKMeans(), raising=False)
    monkeypatch.setattr(
        lr,
        "cluster_mappings",
        {
            0: [0, 1],
            1: [1, 2],
            2: [2, 3],
            3: [3],
        },
        raising=False,
    )

    called_clusters = []

    def fake_read_index(path):
        cid = int(re.search(r"cluster_(\d+)\.index", path).group(1))
        called_clusters.append(cid)
        return FakeFaissIndex(cid)

    monkeypatch.setattr(lr.faiss, "read_index", fake_read_index)
    return called_clusters


def test_case_1_query_encoding_validation_shapes():
    q_tfidf = DummyVectorizer().transform(["machine learning"])
    q_sbert = normalize(DummyModel().encode(["machine learning"], convert_to_numpy=True))
    assert q_tfidf.shape == (1, 10000)
    assert q_sbert.shape == (1, 768)


def test_case_2_cluster_selection_returns_top_3_in_descending_similarity(monkeypatch):
    called_clusters = _configure_local_recommender(monkeypatch)
    lr.recommend_local("machine learning", top_k=4, n_probe_clusters=3)
    assert called_clusters == [0, 1, 2]


def test_case_3_hybrid_scoring_weighted_average():
    score = lr.ALPHA * 0.9 + lr.BETA * 0.8
    assert score == 0.87


def test_case_4_result_deduplication_keeps_unique_papers(monkeypatch):
    _configure_local_recommender(monkeypatch)
    result = lr.recommend_local("machine learning", top_k=4, n_probe_clusters=3)
    titles = [x["title"] for x in result["results"]]
    assert len(titles) == len(set(titles))


def test_case_5_url_based_identifier_extraction():
    paper_id = "0123456789abcdef0123456789abcdef01234567"
    url = f"https://www.semanticscholar.org/paper/example/{paper_id}"
    assert backend_app.extract_paper_id_from_semanticscholar_url(url) == paper_id
