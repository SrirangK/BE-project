from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
from difflib import SequenceMatcher
import requests
import re
import uuid
import threading
import os
from local_recommender import init_local_recommender, recommend_local

S2_BASE = "https://api.semanticscholar.org"
S2_API_KEY = os.getenv("S2_API_KEY")
WEB_TIMEOUT = 8
WEB_TOP_K_DEFAULT = 10

S2_HEADERS = {}
if S2_API_KEY:
    S2_HEADERS["x-api-key"] = S2_API_KEY

app = FastAPI(title="Hybrid Paper Recommendation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PaperCard(BaseModel):
    source: Literal["local", "web_bulk", "seed_reco"]
    paper_id: Optional[str] = None
    title: str
    year: Optional[int] = None
    abstract: Optional[str] = None
    url: Optional[str] = None
    open_access_pdf: Optional[str] = None
    citations: Optional[int] = None
    relevance_score: Optional[float] = None
    author_h_index: Optional[int] = None

class RecommendResponse(BaseModel):
    sectionA: List[PaperCard]
    cluster_id: Optional[int] = None
    cluster_keywords: List[str] = []
    web_job_id: str

class WebResultsResponse(BaseModel):
    status: Literal["loading", "done", "failed"]
    sectionB: List[PaperCard] = []
    error: Optional[str] = None

class SeedRequest(BaseModel):
    seed_input: str
    limit: int = 10

class SeedResponse(BaseModel):
    resolved_method: str
    resolved_paper_id: Optional[str]
    sectionC: List[PaperCard]
    error: Optional[str] = None

class RefineSelectedRequest(BaseModel):
    positive_paper_ids: List[str]
    limit: int = 10

class RefineSelectedResponse(BaseModel):
    used_paper_ids: List[str]
    sectionC: List[PaperCard]
    error: Optional[str] = None

WEB_JOBS: Dict[str, Dict[str, Any]] = {}

def create_job():
    jid = str(uuid.uuid4())
    WEB_JOBS[jid] = {"status": "loading", "results": [], "error": None}
    return jid

def set_job_done(jid, results):
    WEB_JOBS[jid] = {"status": "done", "results": results, "error": None}

def set_job_failed(jid, error):
    WEB_JOBS[jid] = {"status": "failed", "results": [], "error": error}

def get_job(jid):
    return WEB_JOBS.get(jid, {"status": "failed", "results": [], "error": "Invalid job_id"})

def _s2_get(path, params=None, timeout=WEB_TIMEOUT):
    r = requests.get(f"{S2_BASE}{path}", headers=S2_HEADERS, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()

def _s2_post(path, params=None, payload=None, timeout=WEB_TIMEOUT):
    r = requests.post(f"{S2_BASE}{path}", headers=S2_HEADERS, params=params, json=payload, timeout=timeout)
    r.raise_for_status()
    return r.json()

def map_s2_paper_to_card(p: dict, source: str):
    oa = p.get("openAccessPdf") or {}
    return {
        "source": source,
        "paper_id": p.get("paperId"),
        "title": p.get("title", "Untitled"),
        "year": p.get("year"),
        "abstract": p.get("abstract"),
        "url": p.get("url"),
        "open_access_pdf": oa.get("url"),
        "citations": p.get("citationCount"),
        "relevance_score": None,
        "author_h_index": None
    }

def extract_paper_id_from_semanticscholar_url(text: str):
    m = re.search(r"semanticscholar\.org/paper/.+?/([a-f0-9]{40})", text)
    return m.group(1) if m else None

def extract_arxiv_id(text: str):
    m = re.search(r"arxiv\.org/(abs|pdf)/([0-9]{4}\.[0-9]{4,5})(v\d+)?", text)
    if m:
        return m.group(2)
    m2 = re.search(r"\b([0-9]{4}\.[0-9]{4,5})(v\d+)?\b", text)
    return m2.group(1) if m2 else None

def extract_doi(text: str):
    m = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", text, flags=re.I)
    return m.group(0) if m else None

def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", s.lower())).strip()

def _sim(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()

def _title_variants(s: str) -> List[str]:
    base = re.sub(r"\s+", " ", s).strip()
    no_quotes = base.strip("\"'")
    no_trailing_year = re.sub(r"\s*\(?\b(19|20)\d{2}\b\)?\s*$", "", no_quotes).strip()

    variants = [base, no_quotes, no_trailing_year]
    seen = set()
    ordered = []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            ordered.append(v)
    return ordered

def resolve_seed_to_paper_id(seed_input: str):
    s = seed_input.strip()

    # 1) Paper URL
    pid = extract_paper_id_from_semanticscholar_url(s)
    if pid:
        return {"paperId": pid, "method": "paper_url"}

    # 2) DOI
    doi = extract_doi(s)
    if doi:
        try:
            d = _s2_get(f"/graph/v1/paper/DOI:{doi}", params={"fields": "paperId,title,year"})
            if d.get("paperId"):
                return {"paperId": d["paperId"], "method": "doi_lookup"}
        except Exception:
            pass

    # 3) arXiv
    ax = extract_arxiv_id(s)
    if ax:
        try:
            d = _s2_get(f"/graph/v1/paper/ARXIV:{ax}", params={"fields": "paperId,title,year"})
            if d.get("paperId"):
                return {"paperId": d["paperId"], "method": "arxiv_lookup"}
        except Exception:
            pass

    # 4) direct paper id
    if re.fullmatch(r"[a-f0-9]{40}", s.lower()):
        return {"paperId": s.lower(), "method": "direct_paperid"}

    # 5) robust title search
    # First try exact title matcher, then fuzzy search fallback.
    try:
        for q in _title_variants(s):
            try:
                m = _s2_get(
                    "/graph/v1/paper/search/match",
                    params={"query": q, "fields": "paperId,title,year,url"}
                )
                if m.get("paperId"):
                    return {"paperId": m["paperId"], "method": "title_match"}
            except Exception:
                pass

            d = _s2_get(
                "/graph/v1/paper/search",
                params={"query": q, "limit": 10, "fields": "paperId,title,year,url"}
            )
            items = d.get("data", [])
            if not items:
                continue

            # Choose best fuzzy title match.
            scored = []
            for it in items:
                t = it.get("title") or ""
                scored.append((_sim(q, t), it))

            scored.sort(key=lambda x: x[0], reverse=True)
            best_score, best = scored[0]

            # Relaxed threshold; tune if needed.
            if best.get("paperId") and best_score >= 0.40:
                return {"paperId": best["paperId"], "method": f"title_search_fuzzy:{best_score:.2f}"}

            # Fallback: top result anyway.
            if items[0].get("paperId"):
                return {"paperId": items[0]["paperId"], "method": "title_search_top1"}
    except Exception:
        pass

    return {"paperId": None, "method": "unresolved"}

def enrich_author_hindex(cards: List[dict], raw_papers: List[dict]):
    author_ids = []
    for p in raw_papers:
        for a in (p.get("authors") or []):
            aid = a.get("authorId")
            if aid:
                author_ids.append(aid)

    author_ids = list(dict.fromkeys(author_ids))[:200]
    if not author_ids:
        return cards

    try:
        batch = _s2_post("/graph/v1/author/batch",
                         params={"fields": "name,hIndex,paperCount,url"},
                         payload={"ids": author_ids})
        hmap = {x.get("authorId"): x.get("hIndex") for x in batch if x and x.get("authorId")}
        for i, p in enumerate(raw_papers):
            vals = [hmap.get(a.get("authorId")) for a in (p.get("authors") or []) if hmap.get(a.get("authorId")) is not None]
            cards[i]["author_h_index"] = max(vals) if vals else None
    except Exception:
        pass

    return cards

def run_bulk_job(job_id: str, query: str, year_from: int, limit: int):
    try:
        d = _s2_get("/graph/v1/paper/search/bulk", params={
            "query": query,
            "year": f"{year_from}-",
            "fields": "paperId,title,year,abstract,url,citationCount,authors,openAccessPdf"
        })
        papers = d.get("data", [])[:limit]
        cards = [map_s2_paper_to_card(p, "web_bulk") for p in papers]
        cards = enrich_author_hindex(cards, papers)
        set_job_done(job_id, cards)
    except Exception as e:
        set_job_failed(job_id, str(e))

@app.on_event("startup")
def startup_event():
    init_local_recommender()

@app.get("/api/recommend", response_model=RecommendResponse)
def recommend(query: str, top_k: int = 5, year_from: int = 2023, web_limit: int = WEB_TOP_K_DEFAULT):
    local = recommend_local(query, top_k=top_k)
    sectionA = [PaperCard(**x) for x in local["results"]]
    job_id = create_job()
    threading.Thread(target=run_bulk_job, args=(job_id, query, year_from, web_limit), daemon=True).start()
    return RecommendResponse(sectionA=sectionA, cluster_id=local["cluster_id"], cluster_keywords=local["cluster_keywords"], web_job_id=job_id)

@app.get("/api/recommend/web-results", response_model=WebResultsResponse)
def web_results(job_id: str):
    j = get_job(job_id)
    sectionB = [PaperCard(**x) for x in j["results"]] if j["status"] == "done" else []
    return WebResultsResponse(status=j["status"], sectionB=sectionB, error=j["error"])

@app.post("/api/recommend/seed", response_model=SeedResponse)
def recommend_seed(req: SeedRequest):
    resolved = resolve_seed_to_paper_id(req.seed_input)
    pid = resolved["paperId"]
    if not pid:
        return SeedResponse(resolved_method=resolved["method"], resolved_paper_id=None, sectionC=[], error="Could not resolve seed input.")

    d = _s2_post("/recommendations/v1/papers",
                 params={"limit": req.limit, "fields": "paperId,title,year,abstract,url,citationCount,authors,openAccessPdf"},
                 payload={"positivePaperIds": [pid]})
    papers = d.get("recommendedPapers", [])
    cards = [map_s2_paper_to_card(p, "seed_reco") for p in papers]
    cards = enrich_author_hindex(cards, papers)
    return SeedResponse(resolved_method=resolved["method"], resolved_paper_id=pid, sectionC=[PaperCard(**x) for x in cards], error=None)

@app.post("/api/recommend/refine-selected", response_model=RefineSelectedResponse)
def refine_selected(req: RefineSelectedRequest):
    cleaned = []
    seen = set()
    for pid in req.positive_paper_ids:
        p = (pid or "").strip().lower()
        if re.fullmatch(r"[a-f0-9]{40}", p) and p not in seen:
            seen.add(p)
            cleaned.append(p)

    if not cleaned:
        return RefineSelectedResponse(used_paper_ids=[], sectionC=[], error="Select at least one valid paper with a paper ID.")

    d = _s2_post(
        "/recommendations/v1/papers",
        params={"limit": req.limit, "fields": "paperId,title,year,abstract,url,citationCount,authors,openAccessPdf"},
        payload={"positivePaperIds": cleaned[:10]}
    )
    papers = d.get("recommendedPapers", [])
    cards = [map_s2_paper_to_card(p, "seed_reco") for p in papers]
    cards = enrich_author_hindex(cards, papers)
    return RefineSelectedResponse(used_paper_ids=cleaned[:10], sectionC=[PaperCard(**x) for x in cards], error=None)

@app.get("/health")
def health():
    return {"ok": True}
