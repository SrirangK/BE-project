import { useEffect, useRef, useState } from "react";

const API_BASE = "http://localhost:8000";

function PaperCard({ p, index }) {
  return (
    <div style={{ border: "1px solid #ddd", borderRadius: 10, padding: 12, marginBottom: 10 }}>
      <h4>{index + 1}. {p.title}</h4>
      <p><b>Source:</b> {p.source} | <b>Year:</b> {p.year ?? "N/A"}</p>
      <p><b>Relevance score:</b> {p.relevance_score ?? "N/A"} | <b>Citations:</b> {p.citations ?? "N/A"} | <b>Author h-index:</b> {p.author_h_index ?? "N/A"}</p>
      {p.url && <p><a href={p.url} target="_blank" rel="noreferrer">Paper Link</a></p>}
    </div>
  );
}

export default function App() {
  const [query, setQuery] = useState("");
  const [sectionA, setSectionA] = useState([]);
  const [sectionB, setSectionB] = useState([]);
  const [sectionC, setSectionC] = useState([]);
  const [jobId, setJobId] = useState(null);
  const [webStatus, setWebStatus] = useState("idle");
  const [seedInput, setSeedInput] = useState("");
  const [seedInfo, setSeedInfo] = useState("");
  const pollRef = useRef(null);

  const clearPoll = () => { if (pollRef.current) clearInterval(pollRef.current); };

  useEffect(() => () => clearPoll(), []);

  const startPoll = (jid) => {
    setWebStatus("loading");
    pollRef.current = setInterval(async () => {
      const r = await fetch(`${API_BASE}/api/recommend/web-results?job_id=${jid}`);
      const d = await r.json();
      if (d.status === "done") {
        setSectionB(d.sectionB || []);
        setWebStatus("done");
        clearPoll();
      } else if (d.status === "failed") {
        setWebStatus("failed");
        clearPoll();
      }
    }, 1500);
  };

  const handleSearch = async () => {
    clearPoll();
    setSectionA([]); setSectionB([]); setSectionC([]); setSeedInfo("");
    const r = await fetch(`${API_BASE}/api/recommend?query=${encodeURIComponent(query)}&top_k=5`);
    const d = await r.json();
    setSectionA(d.sectionA || []);
    setJobId(d.web_job_id);
    if (d.web_job_id) startPoll(d.web_job_id);
  };

  const handleSeed = async () => {
    const r = await fetch(`${API_BASE}/api/recommend/seed`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ seed_input: seedInput, limit: 10 })
    });
    const d = await r.json();
    setSectionC(d.sectionC || []);
    setSeedInfo(`Resolved by: ${d.resolved_method || "N/A"} | paperId: ${d.resolved_paper_id || "N/A"}`);
  };

  return (
    <div style={{ maxWidth: 900, margin: "20px auto", fontFamily: "Arial" }}>
      <h2>Hybrid Paper Recommendation</h2>

      <textarea
        rows={4}
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter research abstract/description"
        style={{ width: "100%", padding: 8 }}
      />
      <br />
      <button onClick={handleSearch} style={{ marginTop: 8 }}>Get Recommendations</button>

      <hr />
      <h3>Section A: Instant results (local index)</h3>
      {sectionA.map((p, i) => <PaperCard key={`a-${i}`} p={p} index={i} />)}

      <hr />
      <h3>Section B: More relevant results from web (auto-refresh)</h3>
      <p>Status: {webStatus} {jobId ? `| Job: ${jobId}` : ""}</p>
      {sectionB.map((p, i) => <PaperCard key={`b-${i}`} p={p} index={i} />)}

      <hr />
      <h3>Section C: Refine with a seed paper you select</h3>
      <input
        type="text"
        value={seedInput}
        onChange={(e) => setSeedInput(e.target.value)}
        placeholder="Semantic Scholar URL / DOI / arXiv / title"
        style={{ width: "80%", padding: 8 }}
      />
      <button onClick={handleSeed} style={{ marginLeft: 8 }}>Refine</button>
      <p>{seedInfo}</p>
      {sectionC.map((p, i) => <PaperCard key={`c-${i}`} p={p} index={i} />)}
    </div>
  );
}
