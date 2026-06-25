# Before & After: System Architecture Diagram Transformation

## Side-by-Side Comparison

### BEFORE (Tech Stack Focused) ❌

```
┌─────────────────────────────────────────┐
│     OFFLINE PROCESSING PIPELINE         │
├─────────────────────────────────────────┤
│ arXiv Data (38,966 papers)              │
│    ↓                                    │
│ TF-IDF Vectorizer (10K dim)             │
│ SPECTER Embeddings (768 dim)            │
│    ↓                                    │
│ K-Means Clustering (152 clusters)       │
│    ↓                                    │
│ FAISS Indexing (per-cluster)            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ TIER 1: FRONTEND                        │
│ React + Vite (Nginx:3000)               │
│ - QueryInput component                  │
│ - PaperCard component                   │
│ - Refinement component                  │
└─────────────────────────────────────────┘
            ↓ REST API
┌─────────────────────────────────────────┐
│ TIER 2: BACKEND                         │
│ FastAPI (Port 8000)                     │
│ Endpoints:                              │
│ - /recommend                            │
│ - /web-results                          │
│ - /refine                               │
│ - /seed                                 │
│ - /health                               │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ TIER 3: DATA LAYER                      │
│ Offline: TF-IDF, SPECTER, K-Means,      │
│          FAISS                          │
│ Online: Semantic Scholar API            │
└─────────────────────────────────────────┘
```

**Problems:**
- ❌ Too many implementation details
- ❌ Specific technologies mentioned (React, FastAPI, Nginx)
- ❌ Port numbers, dimensions, cluster counts
- ❌ Endpoint URLs visible
- ❌ Component names from code
- ❌ Not reusable if tech changes
- ❌ Looks like a code blueprint, not architecture

---

### AFTER (Module Focused) ✅

```
┌─────────────────────────────────────────┐
│     OFFLINE PROCESSING PIPELINE         │
├─────────────────────────────────────────┤
│ [Paper Corpus]                          │
│    ↓                                    │
│ [Data Ingestion]                        │
│    ↓                                    │
│ [Text Processing]                       │
│    ↓                                    │
│ [Feature Extraction]                    │
│    ↓                                    │
│ [Clustering Module]                     │
│    ↓                                    │
│ [Index Builder]                         │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ PRESENTATION LAYER (Tier 1)             │
│                                         │
│ [Query Interface]                       │
│ [Results Display]                       │
│ [Interaction Handler]                   │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ APPLICATION LAYER (Tier 2)              │
│                                         │
│ [Query Orchestrator]                    │
│     ├─→ [Local Retrieval Engine]       │
│     │     (Path A - Sync)              │
│     ├─→ [Web Discovery Engine]         │
│     │     (Path B - Async)             │
│     └─→ [Refinement Engine]            │
│           (Path C - Sync)              │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│ DATA LAYER (Tier 3)                     │
│                                         │
│ [Offline Data Store]                    │
│ [Job Queue]                             │
│ [External Data Connector]               │
│     ↓                                   │
│ ☁ [External Paper Database]            │
└─────────────────────────────────────────┘
```

**Improvements:**
- ✅ Focus on functional modules
- ✅ No specific technologies
- ✅ No implementation details
- ✅ Clear responsibilities
- ✅ Processing patterns visible (Sync/Async)
- ✅ Reusable even if tech stack changes
- ✅ Looks like proper system architecture

---

## Terminology Mapping

| OLD (Tech Stack) | NEW (Module-Based) |
|------------------|-------------------|
| React + Vite (Nginx:3000) | Query Interface, Results Display |
| FastAPI (Port 8000) | Query Orchestrator, Processing Engines |
| QueryInput component | Query Interface |
| PaperCard component | Results Display |
| /recommend endpoint | Local Retrieval Engine |
| /web-results endpoint | Web Discovery Engine |
| /refine endpoint | Refinement Engine |
| TF-IDF Vectorizer (10K dim) | Feature Extraction Module |
| SPECTER Embeddings (768 dim) | Feature Extraction Module |
| K-Means Clustering (152 clusters) | Clustering Module |
| FAISS Indexing | Index Builder, Offline Data Store |
| Semantic Scholar API | External Paper Database, External Data Connector |
| Job Queue (Redis/in-memory) | Job Queue |
| arXiv Data (38,966 papers) | Paper Corpus |

---

## Label Changes

### Component Names

| Before | After |
|--------|-------|
| "React + Vite" | "Query Interface" |
| "FastAPI" | "Query Orchestrator" |
| "TF-IDF + SPECTER" | "Feature Extraction" |
| "K-Means" | "Clustering Engine" |
| "FAISS" | "Index Builder" |
| "S2 API" | "External Data Connector" |

### Processing Details

| Before | After |
|--------|-------|
| "Encode Query (TF-IDF + SPECTER)" | "Hybrid Query Encoding" |
| "Select Top-3 Clusters" | "Cluster Selection" |
| "FAISS Search" | "Similarity Search" |
| "Hybrid Score (0.7/0.3)" | "Hybrid Scoring" |
| "Query S2 API → Poll Status (2s)" | "Asynchronous Web Query" |
| "Resolve IDs (URL/DOI/arXiv/Title)" | "Identifier Resolution" |

### Section Labels

| Before | After |
|--------|-------|
| "TIER 1: FRONTEND (Blue)" | "PRESENTATION LAYER" |
| "TIER 2: BACKEND (Green)" | "APPLICATION LAYER" |
| "TIER 3: DATA LAYER (Yellow)" | "DATA LAYER" |
| "React + Vite (Nginx:3000)" | [Removed - describe tier purpose instead] |
| "FastAPI (Port 8000)" | [Removed - describe tier purpose instead] |

---

## What to Keep vs. Remove

### ✅ KEEP (These are architectural concepts)

- Tier structure (1/2/3)
- Module names (generic)
- Data flow arrows
- Processing patterns (Sync/Async)
- Path labels (A/B/C)
- External system references
- Layer separation
- Offline vs. Online distinction

### ❌ REMOVE (These are implementation details)

- Framework names (React, FastAPI, Vite)
- Library names (TF-IDF, SPECTER, FAISS, K-Means)
- Port numbers (3000, 8000)
- Server configs (Nginx)
- Endpoint URLs (/recommend, /web-results)
- Dimensions (10K dim, 768 dim)
- Counts (38,966 papers, 152 clusters)
- Component class names (QueryInput, PaperCard)
- Polling intervals (2s)
- Score weights (0.7/0.3)

---

## Where to Put the Details You Removed?

Don't worry! You can still document all these details elsewhere:

### 1. Implementation Details Table (in paper text)

```latex
\begin{table}[h]
\caption{Technology Stack}
\begin{tabular}{ll}
\hline
Layer & Technologies \\
\hline
Frontend & React 18, Vite 4.x, Nginx \\
Backend & FastAPI 0.95, Python 3.10 \\
Feature Extraction & TF-IDF (10K dim), SPECTER (768 dim) \\
Clustering & K-Means (152 clusters) \\
Indexing & FAISS (per-cluster indices) \\
External API & Semantic Scholar API v1 \\
\hline
\end{tabular}
\end{table}
```

### 2. Supplementary Diagram (optional)

Create a second diagram titled "Implementation View" or "Technology Stack" with all the details.

Keep the main "System Architecture" diagram abstract.

### 3. Appendix

Add an appendix section:
- "Appendix A: Technology Choices"
- "Appendix B: Implementation Parameters"
- "Appendix C: API Endpoints"

---

## Benefits of Module-Based Approach

### Academic Benefits
1. **Clarity:** Focus on architecture, not code
2. **Generalizability:** Other researchers can adapt your approach
3. **Professionalism:** Looks like proper system design
4. **Timelessness:** Won't look outdated when frameworks change

### Practical Benefits
1. **Reusability:** Diagram stays valid even if you swap React for Vue
2. **Communication:** Non-technical stakeholders understand it
3. **Documentation:** Captures "what" not "how"
4. **Design thinking:** Forces you to think architecturally

### Presentation Benefits
1. **Less clutter:** More whitespace, easier to read
2. **Better for slides:** Scales well when projected
3. **Focus:** Audience sees structure, not distracting details
4. **Questions:** Reviewers ask about design, not tech choices

---

## Real-World Examples

### Google's Architecture Papers
- Show: "Indexing Service", "Query Processor", "Ranking Engine"
- Don't show: C++, Bigtable cluster size, specific algorithms

### Netflix Architecture Talks
- Show: "Recommendation Service", "Content Delivery", "User Service"
- Don't show: Java versions, Kafka partition counts, specific libraries

### AWS Whitepapers
- Show: "Compute Layer", "Storage Layer", "Network Layer"
- Don't show: EC2 instance types, EBS volume sizes, specific configs

**Your paper should follow the same pattern!**

---

## Final Checklist

Before submitting your new diagram, verify:

- [ ] No framework names (React, Vue, Angular, FastAPI, Flask, etc.)
- [ ] No library names (TF-IDF, SPECTER, FAISS, scikit-learn, etc.)
- [ ] No port numbers (3000, 8000, etc.)
- [ ] No endpoints (/recommend, /api/*, etc.)
- [ ] No dimensions (10K dim, 768 dim, etc.)
- [ ] No counts (152 clusters, 38,966 papers, etc.)
- [ ] No component class names from code
- [ ] Module names describe functionality
- [ ] Tiers/layers are clearly separated
- [ ] Data flow is obvious
- [ ] External systems are marked
- [ ] Processing patterns are labeled (Sync/Async)
- [ ] Color coding is meaningful
- [ ] Legend is included
- [ ] Readable when printed on A4 paper

---

## Summary

**Before:** Code-level view with implementation details
**After:** Architecture-level view with functional modules

The new diagram is cleaner, more professional, and more appropriate for academic/research presentation. 🎯
