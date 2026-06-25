import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

const API_BASE = "http://localhost:8000";
const PAPER_ID_RE = /^[a-f0-9]{40}$/i;

function StatusPill({ tone = "neutral", children }) {
  return <span className={`status-pill ${tone}`}>{children}</span>;
}

function Spinner({ label }) {
  return (
    <div className="spinner-wrap" role="status" aria-live="polite">
      <span className="spinner" aria-hidden="true" />
      <span>{label}</span>
    </div>
  );
}

function ScopusBadge({ value }) {
  if (value === true) return <span className="badge scopus-yes">Scopus ✓</span>;
  if (value === false) return <span className="badge scopus-no">Not in Scopus</span>;
  return null; // null/undefined => unknown => no badge
}

function PaperCard({ p, index, selectable = false, checked = false, onToggle = null }) {
  const hasValidPaperId = !!p.paper_id && PAPER_ID_RE.test(p.paper_id);
  const citationDisplay = p.citations === 0 ? "N/A" : p.citations ?? "N/A";

  return (
    <article className="paper-card" style={{ "--stagger": `${index * 40}ms` }}>
      {selectable && (
        <label className="select-label">
          <input
            type="checkbox"
            disabled={!hasValidPaperId}
            checked={checked}
            onChange={() => onToggle && onToggle(p.paper_id)}
          />
          <span>{hasValidPaperId ? "Use this paper for refine" : "Missing paper ID"}</span>
        </label>
      )}
      <h4>{index + 1}. {p.title}</h4>
      <div className="meta-row">
        <span>Year: {p.year ?? "N/A"}</span>
        {p.venue ? <span className="venue">· {p.venue}</span> : null}
        <ScopusBadge value={p.scopus_indexed} />
      </div>
      <div className="metrics-grid">
        <div><span>Relevance</span><strong>{p.relevance_score ?? "N/A"}</strong></div>
        <div><span>Citations</span><strong>{citationDisplay}</strong></div>
        <div><span>Author h-index</span><strong>{p.author_h_index ?? "N/A"}</strong></div>
      </div>
      {p.url && (
        <p className="card-link">
          <a href={p.url} target="_blank" rel="noreferrer">Open paper</a>
        </p>
      )}
    </article>
  );
}

const EMPTY_FILTERS = { minCitations: "", minRelevance: 0, sinceYear: "", scopusOnly: false };

// Keep cards whose KNOWN values pass; never hide a card for a missing (N/A) value.
// Exception: the explicit "Scopus only" toggle shows confirmed-Scopus cards only.
function makeFilter(f) {
  const minCit = f.minCitations === "" ? null : Number(f.minCitations);
  const minRel = Number(f.minRelevance) || 0;
  const since = f.sinceYear === "" ? null : Number(f.sinceYear);
  return (p) => {
    if (minCit != null && p.citations != null && p.citations < minCit) return false;
    if (minRel > 0 && p.relevance_score != null && p.relevance_score < minRel) return false;
    if (since != null && p.year != null && p.year < since) return false;
    if (f.scopusOnly && p.scopus_indexed !== true) return false;
    return true;
  };
}

export default function App() {
  const [query, setQuery] = useState("");
  const [sectionA, setSectionA] = useState([]);
  const [sectionB, setSectionB] = useState([]);
  const [sectionC, setSectionC] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [webStatus, setWebStatus] = useState("idle");
  const [enrichStatus, setEnrichStatus] = useState("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [selectedPaperIds, setSelectedPaperIds] = useState([]);
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [webDisplayCount, setWebDisplayCount] = useState("10");
  const pollRef = useRef(null);
  const enrichPollRef = useRef(null);

  const clearPolls = () => {
    if (pollRef.current) clearInterval(pollRef.current);
    if (enrichPollRef.current) clearInterval(enrichPollRef.current);
  };

  useEffect(() => () => clearPolls(), []);

  const startPoll = (jid) => {
    setWebStatus("loading");
    pollRef.current = setInterval(async () => {
      try {
        const r = await fetch(`${API_BASE}/api/recommend/web-results?job_id=${jid}`);
        const d = await r.json();
        if (d.status === "done") {
          setSectionB(d.sectionB || []);
          setWebStatus("done");
          clearInterval(pollRef.current);
        } else if (d.status === "failed") {
          setWebStatus("failed");
          setErrorMessage(d.error || "Web search failed.");
          clearInterval(pollRef.current);
        }
      } catch (error) {
        setWebStatus("failed");
        setErrorMessage(error.message || "Failed to fetch web results.");
        clearInterval(pollRef.current);
      }
    }, 1500);
  };

  const startEnrichPoll = (jid) => {
    setEnrichStatus("loading");
    enrichPollRef.current = setInterval(async () => {
      try {
        const r = await fetch(`${API_BASE}/api/recommend/local-enriched?job_id=${jid}`);
        const d = await r.json();
        if (d.status === "done") {
          if (d.sectionA && d.sectionA.length) setSectionA(d.sectionA);
          setEnrichStatus("done");
          clearInterval(enrichPollRef.current);
        } else if (d.status === "failed") {
          setEnrichStatus("failed");
          clearInterval(enrichPollRef.current);
        }
      } catch (error) {
        setEnrichStatus("failed");
        clearInterval(enrichPollRef.current);
      }
    }, 1500);
  };

  const handleSearch = async () => {
    clearPolls();
    setSectionA([]); setSectionB([]); setSectionC([]);
    setSelectedPaperIds([]);
    setErrorMessage("");
    setIsSearching(true);
    setWebStatus("idle");
    setEnrichStatus("idle");

    try {
      const r = await fetch(`${API_BASE}/api/recommend?query=${encodeURIComponent(query)}&top_k=5`);
      if (!r.ok) throw new Error("Search request failed.");
      const d = await r.json();
      setSectionA(d.sectionA || []);
      setJobId(d.web_job_id);
      if (d.web_job_id) startPoll(d.web_job_id);
      else setWebStatus("idle");
      if (d.enrich_job_id) startEnrichPoll(d.enrich_job_id);
    } catch (error) {
      setErrorMessage(error.message || "Unable to get recommendations.");
    } finally {
      setIsSearching(false);
    }
  };

  const toggleSelected = (paperId) => {
    if (!paperId || !PAPER_ID_RE.test(paperId)) return;
    setSelectedPaperIds((prev) => {
      const id = paperId.toLowerCase();
      return prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id];
    });
  };

  const handleRefineSelected = async () => {
    setErrorMessage("");
    setIsRefining(true);
    try {
      const r = await fetch(`${API_BASE}/api/recommend/refine-selected`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ positive_paper_ids: selectedPaperIds, limit: 10 })
      });
      const d = await r.json();
      setSectionC(d.sectionC || []);
      if (d.error) {
        setErrorMessage(d.error);
      }
    } catch (error) {
      setErrorMessage(error.message || "Refine from selection failed.");
    } finally {
      setIsRefining(false);
    }
  };

  const selectedCount = selectedPaperIds.length;
  const canSearch = query.trim().length > 0 && !isSearching;
  const canRefineSelected = selectedCount > 0 && !isRefining;

  const filterFn = useMemo(() => makeFilter(filters), [filters]);
  const filteredA = useMemo(() => sectionA.filter(filterFn), [sectionA, filterFn]);
  const filteredB = useMemo(() => sectionB.filter(filterFn), [sectionB, filterFn]);
  const filteredC = useMemo(() => sectionC.filter(filterFn), [sectionC, filterFn]);
  const displayedB = useMemo(() => {
    if (webDisplayCount === "all") return filteredB;
    return filteredB.slice(0, Number(webDisplayCount));
  }, [filteredB, webDisplayCount]);

  const setFilter = (key, value) => setFilters((prev) => ({ ...prev, [key]: value }));
  const filtersActive =
    filters.minCitations !== "" || Number(filters.minRelevance) > 0 ||
    filters.sinceYear !== "" || filters.scopusOnly;

  return (
    <div className="page-bg">
      <div className="ambient a" />
      <div className="ambient b" />

      <main className="app-shell">
        <header className="hero">
          <p className="kicker">Research Assistant</p>
          <h1>Hybrid Paper Recommendation</h1>
          <p className="sub">Search faster, select stronger papers, and refine recommendations from your curated picks.</p>
        </header>

        {errorMessage && <div className="alert error">{errorMessage}</div>}

        <section className="panel">
          <h2>1. Discover papers</h2>
          <p className="panel-sub">Paste your abstract or topic statement.</p>
          <textarea
            rows={5}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Example: Parameter-efficient adapters for multimodal transformers in radiology"
            className="query-box"
          />
          <div className="actions-row">
            <button className="btn primary" disabled={!canSearch} onClick={handleSearch}>
              {isSearching ? "Searching..." : "Get Recommendations"}
            </button>
            {isSearching && <Spinner label="Analyzing your prompt" />}
          </div>
        </section>

        <section className="panel">
          <div className="section-head">
            <h2>Filters</h2>
            {filtersActive && (
              <button className="btn ghost btn-sm" onClick={() => setFilters(EMPTY_FILTERS)}>Reset</button>
            )}
          </div>
          <p className="panel-sub">Applied to all results below. Papers missing a value (N/A) are not hidden.</p>
          <div className="filter-bar">
            <label className="filter-field">
              <span>Min citations</span>
              <input
                type="number" min="0" placeholder="any"
                value={filters.minCitations}
                onChange={(e) => setFilter("minCitations", e.target.value)}
              />
            </label>
            <label className="filter-field">
              <span>Min relevance: <strong className="range-val">{Number(filters.minRelevance).toFixed(2)}</strong></span>
              <input
                type="range" min="0" max="1" step="0.05"
                value={filters.minRelevance}
                onChange={(e) => setFilter("minRelevance", e.target.value)}
              />
            </label>
            <label className="filter-field">
              <span>Published since (year)</span>
              <input
                type="number" min="1900" max="2100" placeholder="any"
                value={filters.sinceYear}
                onChange={(e) => setFilter("sinceYear", e.target.value)}
              />
            </label>
            <label className="filter-field checkbox-field">
              <span>Scopus only</span>
              <input
                type="checkbox"
                checked={filters.scopusOnly}
                onChange={(e) => setFilter("scopusOnly", e.target.checked)}
              />
            </label>
          </div>
        </section>

        <section className="panel">
          <div className="section-head">
            <h2>2. Select papers to refine</h2>
            <StatusPill tone={selectedCount > 0 ? "good" : "neutral"}>Selected: {selectedCount}</StatusPill>
          </div>
          <p className="panel-sub">Tick papers from local and web results, then refine from your selections.</p>

          <div className="section-head">
            <h3>Local results</h3>
            {enrichStatus === "loading" && <Spinner label="Enriching metadata…" />}
          </div>
          {filteredA.length === 0 && !isSearching ? <p className="empty">No local results yet.</p> : null}
          {filteredA.map((p, i) => (
            <PaperCard
              key={`a-${i}`}
              p={p}
              index={i}
              selectable
              checked={!!p.paper_id && selectedPaperIds.includes(String(p.paper_id).toLowerCase())}
              onToggle={toggleSelected}
            />
          ))}

          <div className="section-head web-head">
            <h3>Web results</h3>
            <div className="web-controls">
              {sectionB.length > 0 && (
                <label className="count-select">
                  <span>Show</span>
                  <select value={webDisplayCount} onChange={(e) => setWebDisplayCount(e.target.value)}>
                    <option value="10">10</option>
                    <option value="25">25</option>
                    <option value="50">50</option>
                    <option value="all">All</option>
                  </select>
                </label>
              )}
              <StatusPill tone={webStatus === "done" ? "good" : webStatus === "failed" ? "bad" : "neutral"}>
                {webStatus}
              </StatusPill>
            </div>
          </div>
          {sectionB.length > 0 && (
            <p className="job">Showing {displayedB.length} of {filteredB.length} matching ({sectionB.length} fetched)</p>
          )}
          {webStatus === "loading" ? <Spinner label="Fetching additional papers from web" /> : null}
          {sectionB.length === 0 && webStatus !== "loading" ? <p className="empty">No web results yet.</p> : null}
          {displayedB.map((p, i) => (
            <PaperCard
              key={`b-${i}`}
              p={p}
              index={i}
              selectable
              checked={!!p.paper_id && selectedPaperIds.includes(String(p.paper_id).toLowerCase())}
              onToggle={toggleSelected}
            />
          ))}

          <div className="actions-row">
            <button className="btn secondary" disabled={!canRefineSelected} onClick={handleRefineSelected}>
              {isRefining ? "Refining..." : "Refine from selected papers"}
            </button>
            {isRefining ? <Spinner label="Generating refined recommendations" /> : null}
          </div>
        </section>

        <section className="panel info-panel">
          <h2>About the metrics</h2>
          <div className="metrics-help">
            <div className="help-item">
              <strong>Relevance:</strong> For local results, a 0-1 hybrid similarity to your query. For web/refined results, a normalized rank position (top = 1.0).
            </div>
            <div className="help-item">
              <strong>Citations:</strong> Number of times this paper has been cited by other works. Higher usually indicates impact.
            </div>
            <div className="help-item">
              <strong>Author h-index:</strong> Measure of an author's prolific and cited research. Higher values indicate more influential researchers.
            </div>
            <div className="help-item">
              <strong>Scopus ✓:</strong> The paper's venue is indexed in Scopus (a reputation signal). No badge means the venue could not be verified.
            </div>
          </div>
        </section>

        <section className="panel">
          <h2>Refined recommendations</h2>
          {filteredC.length === 0 ? <p className="empty">Your refined recommendations will appear here.</p> : null}
          {filteredC.map((p, i) => <PaperCard key={`c-${i}`} p={p} index={i} />)}
        </section>
      </main>
    </div>
  );
}
