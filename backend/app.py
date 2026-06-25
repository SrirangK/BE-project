from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Literal
from difflib import SequenceMatcher
from concurrent.futures import ThreadPoolExecutor
import requests
import re
import uuid
import threading
import time
import os
from local_recommender import init_local_recommender, recommend_local
from scopus_index import is_scopus_indexed, load_scopus_issns

S2_BASE = "https://api.semanticscholar.org"
S2_API_KEY = os.getenv("S2_API_KEY")
WEB_TIMEOUT = 8
WEB_TOP_K_DEFAULT = 10
WEB_POOL_DEFAULT = 100        # large pool fetched from S2; frontend chooses how many to show
ENRICH_MAX_WORKERS = 5        # bound concurrent S2 title-resolution calls (rate-limit safety)
# Shared field set for S2 paper queries (adds venue/issn/doi for Scopus detection).
S2_FIELDS = "paperId,title,year,abstract,url,citationCount,authors,openAccessPdf,externalIds,publicationVenue,venue"

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
    venue: Optional[str] = None
    scopus_indexed: Optional[bool] = None

class RecommendResponse(BaseModel):
    sectionA: List[PaperCard]
    cluster_id: Optional[int] = None
    cluster_keywords: List[str] = []
    web_job_id: str
    enrich_job_id: str

class WebResultsResponse(BaseModel):
    status: Literal["loading", "done", "failed"]
    sectionB: List[PaperCard] = []
    error: Optional[str] = None

class LocalEnrichedResponse(BaseModel):
    status: Literal["loading", "done", "failed"]
    sectionA: List[PaperCard] = []
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

# Global throttle: unauthenticated Semantic Scholar is heavily rate-limited (~1 rps,
# shared). Pace all S2 traffic and retry on 429 so concurrent web + enrich jobs don't
# starve each other. An S2_API_KEY raises the real limit; we still pace politely.
_S2_LOCK = threading.Lock()
_S2_LAST = [0.0]
_S2_MIN_INTERVAL = 0.5 if S2_API_KEY else 1.0

def _s2_throttle():
    with _S2_LOCK:
        wait = _S2_MIN_INTERVAL - (time.monotonic() - _S2_LAST[0])
        if wait > 0:
            time.sleep(wait)
        _S2_LAST[0] = time.monotonic()

def _s2_request(method, path, params=None, payload=None, timeout=WEB_TIMEOUT, retries=3):
    for attempt in range(retries + 1):
        _s2_throttle()
        try:
            if method == "POST":
                r = requests.post(f"{S2_BASE}{path}", headers=S2_HEADERS, params=params, json=payload, timeout=timeout)
            else:
                r = requests.get(f"{S2_BASE}{path}", headers=S2_HEADERS, params=params, timeout=timeout)
        except (requests.ConnectionError, requests.Timeout):
            if attempt < retries:
                time.sleep(1.0 * (attempt + 1))
                continue
            raise
        if r.status_code == 429 and attempt < retries:
            time.sleep(1.5 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()

def _s2_get(path, params=None, timeout=WEB_TIMEOUT):
    return _s2_request("GET", path, params=params, timeout=timeout)

def _s2_post(path, params=None, payload=None, timeout=WEB_TIMEOUT):
    return _s2_request("POST", path, params=params, payload=payload, timeout=timeout)

def _venue_issns(p: dict):
    """Pull (issns, venue_name) from an S2 paper's publicationVenue/venue fields.

    S2 returns publicationVenue as a structured object on some endpoints but as a
    plain string (or omits it) on others, so handle dict / str / None defensively.
    """
    pv = p.get("publicationVenue")
    issns = []
    venue = None
    if isinstance(pv, dict):
        if pv.get("issn"):
            issns.append(pv["issn"])
        issns.extend(pv.get("alternate_issns") or [])
        venue = pv.get("name")
    # When publicationVenue is a string it is an opaque venue ID (UUID), not a name,
    # and carries no ISSN — ignore it and use the plain `venue` field for the name.
    v = p.get("venue")
    if not venue and isinstance(v, str) and v:
        venue = v
    return issns, venue

def map_s2_paper_to_card(p: dict, source: str):
    oa = p.get("openAccessPdf") or {}
    issns, venue = _venue_issns(p)
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
        "author_h_index": None,
        "venue": venue,
        "scopus_indexed": is_scopus_indexed(issns, venue),
    }

def apply_rank_relevance(cards: List[dict]):
    """Assign a normalized-rank relevance proxy (top result = 1.0) for S2 results."""
    n = len(cards)
    for i, c in enumerate(cards):
        c["relevance_score"] = round((n - i) / n, 4) if n else None
    return cards

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
            "fields": S2_FIELDS
        })
        papers = d.get("data", [])[:limit]
        cards = [map_s2_paper_to_card(p, "web_bulk") for p in papers]
        cards = enrich_author_hindex(cards, papers)
        apply_rank_relevance(cards)
        set_job_done(job_id, cards)
    except Exception as e:
        set_job_failed(job_id, str(e))

# --- Local (arXiv) result enrichment: resolve title -> S2 -> fill metadata ---
ENRICH_CACHE: Dict[str, dict] = {}      # normalized title -> metadata dict
ENRICH_LOCK = threading.Lock()
_META_KEYS = ("paper_id", "year", "citations", "url", "open_access_pdf",
              "venue", "scopus_indexed", "author_h_index")

def _resolve_title_to_pid(title: str):
    """Resolve a paper title to an S2 paperId using the title-match endpoint only
    (one request; the match endpoint returns candidates under `data`)."""
    title = (title or "").strip()
    if not title:
        return None
    try:
        d = _s2_get("/graph/v1/paper/search/match", params={"query": title, "fields": "paperId,title"})
    except Exception:
        return None
    items = (d or {}).get("data") or []
    if not items:
        return None
    best = items[0]
    pid = best.get("paperId")
    if pid and _sim(title, best.get("title") or "") >= 0.6:
        return pid
    return None

def _merge_meta(local_card: dict, raw: dict):
    """Overlay S2 metadata onto a local card (preserving title/abstract/relevance/source)."""
    merged = dict(local_card)
    if not raw:
        return merged
    issns, venue = _venue_issns(raw)
    oa = raw.get("openAccessPdf") or {}
    merged.update({
        "paper_id": raw.get("paperId"),
        "year": raw.get("year"),
        "citations": raw.get("citationCount"),
        "url": raw.get("url"),
        "open_access_pdf": oa.get("url"),
        "venue": venue,
        "scopus_indexed": is_scopus_indexed(issns, venue),
        "abstract": local_card.get("abstract") or raw.get("abstract"),
    })
    return merged

def run_local_enrich_job(job_id: str, local_results: List[dict]):
    try:
        keys = [_norm(c.get("title") or "") for c in local_results]

        # 1) cache lookup
        with ENRICH_LOCK:
            cached = {k: ENRICH_CACHE.get(k) for k in keys}
        miss_idx = [i for i, k in enumerate(keys) if not cached.get(k)]

        # 2) resolve titles -> paperIds (bounded concurrency), then one batch metadata fetch
        if miss_idx:
            with ThreadPoolExecutor(max_workers=ENRICH_MAX_WORKERS) as ex:
                pids = list(ex.map(
                    lambda i: _resolve_title_to_pid(local_results[i].get("title") or ""),
                    miss_idx
                ))
            id_for_idx = {miss_idx[j]: pids[j] for j in range(len(miss_idx))}
            unique_ids = list(dict.fromkeys([p for p in pids if p]))

            raw_by_id = {}
            if unique_ids:
                try:
                    batch = _s2_post("/graph/v1/paper/batch",
                                     params={"fields": S2_FIELDS},
                                     payload={"ids": unique_ids})
                    for item in (batch or []):
                        if item and item.get("paperId"):
                            raw_by_id[item["paperId"]] = item
                except Exception:
                    pass

            miss_cards, miss_raw = [], []
            for i in miss_idx:
                raw = raw_by_id.get(id_for_idx.get(i)) or {}
                miss_cards.append(_merge_meta(local_results[i], raw))
                miss_raw.append(raw)
            enrich_author_hindex(miss_cards, miss_raw)

            # cache only successful resolutions so transient failures retry later
            with ENRICH_LOCK:
                for pos, i in enumerate(miss_idx):
                    meta = {k: miss_cards[pos].get(k) for k in _META_KEYS}
                    if meta.get("paper_id"):
                        ENRICH_CACHE[keys[i]] = meta
                    cached[keys[i]] = meta

        # 3) overlay metadata onto every local card (keep known local values otherwise)
        enriched = []
        for i, c in enumerate(local_results):
            meta = cached.get(keys[i]) or {}
            enriched.append({**c, **{k: v for k, v in meta.items() if v is not None}})
        set_job_done(job_id, enriched)
    except Exception as e:
        set_job_failed(job_id, str(e))

@app.on_event("startup")
def startup_event():
    init_local_recommender()
    load_scopus_issns()

@app.get("/api/recommend", response_model=RecommendResponse)
def recommend(query: str, top_k: int = 5, year_from: int = 2023, web_limit: int = WEB_POOL_DEFAULT):
    local = recommend_local(query, top_k=top_k)
    sectionA = [PaperCard(**x) for x in local["results"]]

    web_job_id = create_job()
    enrich_job_id = create_job()
    threading.Thread(target=run_bulk_job, args=(web_job_id, query, year_from, web_limit), daemon=True).start()
    threading.Thread(target=run_local_enrich_job, args=(enrich_job_id, local["results"]), daemon=True).start()

    return RecommendResponse(
        sectionA=sectionA,
        cluster_id=local["cluster_id"],
        cluster_keywords=local["cluster_keywords"],
        web_job_id=web_job_id,
        enrich_job_id=enrich_job_id,
    )

@app.get("/api/recommend/web-results", response_model=WebResultsResponse)
def web_results(job_id: str):
    j = get_job(job_id)
    sectionB = [PaperCard(**x) for x in j["results"]] if j["status"] == "done" else []
    return WebResultsResponse(status=j["status"], sectionB=sectionB, error=j["error"])

@app.get("/api/recommend/local-enriched", response_model=LocalEnrichedResponse)
def local_enriched(job_id: str):
    j = get_job(job_id)
    sectionA = [PaperCard(**x) for x in j["results"]] if j["status"] == "done" else []
    return LocalEnrichedResponse(status=j["status"], sectionA=sectionA, error=j["error"])

@app.post("/api/recommend/seed", response_model=SeedResponse)
def recommend_seed(req: SeedRequest):
    resolved = resolve_seed_to_paper_id(req.seed_input)
    pid = resolved["paperId"]
    if not pid:
        return SeedResponse(resolved_method=resolved["method"], resolved_paper_id=None, sectionC=[], error="Could not resolve seed input.")

    d = _s2_post("/recommendations/v1/papers",
                 params={"limit": req.limit, "fields": S2_FIELDS},
                 payload={"positivePaperIds": [pid]})
    papers = d.get("recommendedPapers", [])
    cards = [map_s2_paper_to_card(p, "seed_reco") for p in papers]
    cards = enrich_author_hindex(cards, papers)
    apply_rank_relevance(cards)
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
        params={"limit": req.limit, "fields": S2_FIELDS},
        payload={"positivePaperIds": cleaned[:10]}
    )
    papers = d.get("recommendedPapers", [])
    cards = [map_s2_paper_to_card(p, "seed_reco") for p in papers]
    cards = enrich_author_hindex(cards, papers)
    apply_rank_relevance(cards)
    return RefineSelectedResponse(used_paper_ids=cleaned[:10], sectionC=[PaperCard(**x) for x in cards], error=None)

@app.get("/health")
def health():
    return {"ok": True}
