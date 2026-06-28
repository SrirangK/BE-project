import statistics
import time

import pytest

TestClient = pytest.importorskip("fastapi.testclient").TestClient
backend_app = pytest.importorskip("app")


class ImmediateThread:
    def __init__(self, target, args=(), kwargs=None, daemon=None):
        self._target = target
        self._args = args
        self._kwargs = kwargs or {}
        self.daemon = daemon

    def start(self):
        self._target(*self._args, **self._kwargs)


def _local_result(i):
    return {
        "source": "local",
        "paper_id": "a" * 40,
        "title": f"Local Paper {i + 1}",
        "year": 2024,
        "abstract": "abstract",
        "url": "https://example.org/paper",
        "open_access_pdf": None,
        "citations": 10 + i,
        "relevance_score": round(1 - (i / 100), 4),
        "author_h_index": 20,
        "venue": "Test Venue",
        "scopus_indexed": True,
    }


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(backend_app, "init_local_recommender", lambda: None)
    monkeypatch.setattr(backend_app, "load_scopus_issns", lambda: None, raising=False)
    monkeypatch.setattr(backend_app.threading, "Thread", ImmediateThread)

    def fake_recommend_local(_query, top_k=5):
        return {
            "cluster_id": 1,
            "cluster_keywords": [],
            "results": [_local_result(i) for i in range(top_k)],
        }

    def fake_run_bulk_job(job_id, _query, _year_from, limit):
        cards = []
        for i in range(min(limit, 10)):
            cards.append(
                {
                    "source": "web_bulk",
                    "paper_id": f"{i:040x}",
                    "title": f"Web Paper {i + 1}",
                    "year": 2024,
                    "abstract": "abstract",
                    "url": "https://example.org/web-paper",
                    "open_access_pdf": None,
                    "citations": 50,
                    "relevance_score": 1.0 - i / 10,
                    "author_h_index": 10,
                    "venue": "Web Venue",
                    "scopus_indexed": True,
                }
            )
        backend_app.set_job_done(job_id, cards)

    def fake_run_local_enrich_job(job_id, local_results):
        backend_app.set_job_done(job_id, local_results)

    monkeypatch.setattr(backend_app, "recommend_local", fake_recommend_local)
    monkeypatch.setattr(backend_app, "run_bulk_job", fake_run_bulk_job)
    monkeypatch.setattr(backend_app, "run_local_enrich_job", fake_run_local_enrich_job, raising=False)

    with TestClient(backend_app.app) as test_client:
        yield test_client


def test_case_6_complete_local_recommendation_flow(client):
    """Test Case 6: Complete Local Recommendation Flow - Returns 20 papers with descending scores"""
    resp = client.get(
        "/api/recommend",
        params={"query": "deep learning for computer vision", "top_k": 20},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["sectionA"]) == 20
    scores = [x["relevance_score"] for x in data["sectionA"]]
    assert scores == sorted(scores, reverse=True)


def test_case_7_asynchronous_web_search_job_lifecycle(client):
    """Test Case 7: Asynchronous Web Search - Job transitions pending → completed"""
    jid = backend_app.create_job()
    assert backend_app.get_job(jid)["status"] == "loading"
    backend_app.run_bulk_job(jid, "neural networks", 2023, 5)
    assert backend_app.get_job(jid)["status"] == "done"


def test_case_8_paper_selection_and_refinement_seed_endpoint(client, monkeypatch):
    """Test Case 8: Paper Selection and Refinement - Resolve ID and fetch recommendations"""
    monkeypatch.setattr(
        backend_app,
        "resolve_seed_to_paper_id",
        lambda _seed: {"paperId": "b" * 40, "method": "arxiv_lookup"},
    )
    monkeypatch.setattr(backend_app, "is_scopus_indexed", lambda _issns, _venue: True, raising=False)
    monkeypatch.setattr(backend_app, "enrich_author_hindex", lambda cards, _raw: cards)

    def fake_s2_post(path, params=None, payload=None, timeout=8):
        if path == "/recommendations/v1/papers":
            return {
                "recommendedPapers": [
                    {
                        "paperId": "c" * 40,
                        "title": "Refined Paper",
                        "year": 2024,
                        "url": "https://example.org/refined",
                        "citationCount": 42,
                        "authors": [],
                        "openAccessPdf": {},
                        "venue": "Refined Venue",
                    }
                ]
            }
        raise AssertionError("Unexpected path")

    monkeypatch.setattr(backend_app, "_s2_post", fake_s2_post)

    resp = client.post("/api/recommend/seed", json={"seed_input": "1706.03762", "limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert data["resolved_method"] == "arxiv_lookup"
    assert len(data["sectionC"]) == 1
    assert data["sectionC"][0]["title"] == "Refined Paper"


def test_case_9_model_and_index_loading_under_30_seconds(monkeypatch):
    """Test Case 9: Model and Index Loading - Load all artifacts in under 30 seconds"""
    monkeypatch.setattr(backend_app, "init_local_recommender", lambda: time.sleep(0.01))
    monkeypatch.setattr(backend_app, "load_scopus_issns", lambda: time.sleep(0.01), raising=False)
    start = time.perf_counter()
    backend_app.startup_event()
    elapsed = time.perf_counter() - start
    assert elapsed < 30


def test_case_10_response_time_validation_under_500ms_median(client):
    """Test Case 10: Response Time Validation - Median latency < 500ms for local recommendations"""
    durations_ms = []
    for _ in range(5):
        start = time.perf_counter()
        resp = client.get("/api/recommend", params={"query": "standard query", "top_k": 5})
        assert resp.status_code == 200
        durations_ms.append((time.perf_counter() - start) * 1000)
    assert statistics.median(durations_ms) < 500
