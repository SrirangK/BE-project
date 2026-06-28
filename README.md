# Smart Pre-trained Research Paper Suggestion System

A hybrid recommendation system that combines local FAISS-based vector search with web-based Semantic Scholar recommendations to suggest relevant research papers.

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [System Architecture](#system-architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 📖 Project Overview

This is a **Smart Research Paper Recommendation System** that helps researchers discover relevant papers using two complementary approaches:

### Local Recommendation (White-box)
- Uses TF-IDF vectorization and SPECTER embeddings for semantic search
- K-Means clustering for efficient indexing
- FAISS (Facebook AI Similarity Search) for fast nearest-neighbor lookup
- Hybrid scoring combining semantic similarity and TF-IDF relevance
- Median latency: **~412ms** for 20 results

### Web Recommendation (Black-box)
- Asynchronous jobs to query Semantic Scholar API
- Background processing with status tracking
- Paper enrichment with metadata (citations, h-index, venue info)
- Scopus indexing detection for quality assessment

### UI/UX
- React frontend with real-time search suggestions
- Section A: Local results (immediate, ~1.2s)
- Section B: Web results (background polling, ~10s)
- Special character handling, error validation
- CORS-enabled for cross-origin requests

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      React Frontend                         │
│                    (Vite + JavaScript)                      │
│  ┌──────────────────────┬──────────────────────────────┐   │
│  │   Section A (Local)  │   Section B (Web Results)   │   │
│  │    Results           │    Background Polling      │   │
│  └──────────────────────┴──────────────────────────────┘   │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP/REST (CORS)
┌────────────────▼────────────────────────────────────────────┐
│              FastAPI Backend (Python)                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Local Recommender Module                           │   │
│  │  ├── TF-IDF Vectorizer (10,000 dims)               │   │
│  │  ├── SPECTER Model (768 dims, Transformers)        │   │
│  │  ├── K-Means Clustering (152 clusters)             │   │
│  │  ├── FAISS Indices (152 per-cluster indices)        │   │
│  │  └── Hybrid Scorer (0.7 semantic + 0.3 TF-IDF)     │   │
│  │                                                     │   │
│  │  Web Search Module                                  │   │
│  │  ├── Semantic Scholar API Integration              │   │
│  │  ├── Job Queue (ThreadPoolExecutor)                │   │
│  │  ├── Metadata Enrichment                           │   │
│  │  └── Scopus Index Lookup                           │   │
│  │                                                     │   │
│  │  API Endpoints                                      │   │
│  │  ├── POST /api/recommend                           │   │
│  │  ├── GET /api/recommend/local-enriched             │   │
│  │  ├── POST /api/refine                              │   │
│  │  └── GET /health                                   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Prerequisites

### System Requirements
- **Docker & Docker Compose** (Recommended for consistent environment)
- **Python 3.9+** (if running without Docker)
- **Node.js 16+** (for frontend development)
- **4GB+ RAM** (FAISS indices and models require memory)
- **GPU optional** (CPU-only via PyTorch CPU variant included)

### Required Files
- `backend/artifacts/` - Pre-trained models and indices
  - TF-IDF vectorizer
  - SPECTER model weights
  - K-Means centroids (152 clusters)
  - FAISS indices (152 files)
  - Scopus ISSN mapping
- Models auto-download from Hugging Face on first run

### Optional Environment Variables
```bash
HUGGINGFACE_HUB_TOKEN=hf_xxxx...    # Higher HF rate limits
S2_API_KEY=xxxx...                  # Semantic Scholar API key
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/BE-project.git
cd BE-project

# 2. Start services (backend + frontend)
docker compose up --build

# 3. Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000/docs
# Health check: http://localhost:8000/health
```

**What happens:**
- ✅ Backend starts on port 8000 (FastAPI + Uvicorn)
- ✅ Frontend builds and runs on port 5173 (Vite + Nginx)
- ✅ HuggingFace model cache shared via volume (persistent)
- ✅ CORS enabled for cross-origin requests

### Option 2: Local Development (Without Docker)

**Backend Setup:**
```bash
# Install Python dependencies
cd backend
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

# Start backend server
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Frontend Setup (in new terminal):**
```bash
# Install Node dependencies
cd frontend
npm install

# Start dev server
npm run dev
# Vite runs on http://localhost:5173
```

---

## 📁 Project Structure

```
BE-project/
├── README.md                              # This file
├── docker-compose.yml                     # Docker services orchestration
│
├── backend/                               # FastAPI Python Backend
│   ├── Dockerfile                         # Backend container config
│   ├── requirements.txt                   # Python dependencies
│   ├── app.py                             # Main FastAPI application
│   ├── local_recommender.py               # Local search (TF-IDF + SPECTER + FAISS)
│   ├── scopus_index.py                    # Scopus ISSN indexing
│   ├── artifacts/                         # Pre-trained models & indices
│   │   ├── tfidf_vectorizer.pkl           # TF-IDF model (10,000 dims)
│   │   ├── kmeans_centroids.npy           # K-Means centroids (152 clusters)
│   │   ├── cluster_0.faiss ... 151.faiss  # FAISS indices (per-cluster)
│   │   └── scopus_issns.pkl               # Scopus ISSN mappings
│   ├── tests/                             # Pytest suite (14 test cases)
│   │   ├── test_whitebox.py               # Cases 1-5 (Unit tests)
│   │   └── test_integration.py            # Cases 6-10 (Integration tests)
│   └── __pycache__/                       # Python cache (auto-generated)
│
├── frontend/                              # React + Vite Frontend
│   ├── Dockerfile                         # Frontend container config
│   ├── package.json                       # NPM dependencies & scripts
│   ├── playwright.config.js               # E2E test configuration
│   ├── vite.config.js                     # Vite bundler config
│   ├── index.html                         # Entry HTML
│   ├── nginx.conf                         # Nginx config (production)
│   ├── src/                               # React components
│   │   └── App.jsx                        # Main React app
│   ├── e2e/                               # Playwright E2E tests
│   │   └── functional.spec.ts             # Cases 11-14 (Black-box tests)
│   └── test-results/                      # Playwright reports (auto-generated)
│
├── testing/                               # Test Evidence & Reports
│   ├── evidence/                          # Generated proof artifacts
│   │   ├── pytest-backend-verbose.txt     # Backend test output
│   │   ├── playwright-verbose.txt         # Frontend test output
│   │   ├── junit-backend.xml              # JUnit XML format
│   │   └── pytest-report.html             # HTML report
│   └── .gitkeep
│
└── diagrams/                              # Architecture diagrams
```

---

## 🎯 Running the Application

### Using Docker Compose (Recommended)

**Start Services:**
```bash
# Build and start all services (background)
docker compose up -d

# Or foreground (see logs in real-time)
docker compose up --build
```

**Check Status:**
```bash
# View running containers
docker compose ps

# View logs
docker compose logs backend        # Backend logs
docker compose logs frontend       # Frontend logs
docker compose logs -f backend     # Follow backend logs

# Health check
curl http://localhost:8000/health
```

**Stop Services:**
```bash
# Stop services (keep volumes)
docker compose stop

# Stop and remove containers
docker compose down

# Remove everything including volumes
docker compose down -v
```

### Running Locally (Development)

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# Backend at http://localhost:8000
# API Docs at http://localhost:8000/docs
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
# Frontend at http://localhost:5173
```

**Terminal 3 - Test (Optional):**
```bash
cd backend
python3 -m pytest tests/ -v
```

---

## 🧪 Testing

### Test Coverage Summary

**14 Total Test Cases** aligned with report Section 6.3:

| **Test Type** | **Cases** | **Count** | **Status** |
|---|---|---|---|
| **White-Box (Unit)** | 1-5 | 5 | ✅ PASS |
| **Integration** | 6-10 | 5 | ✅ PASS |
| **Black-Box (Functional)** | 11-14 | 4 | ✅ PASS |
| **TOTAL** | — | **14** | **✅ 14/14 PASS** |

### Backend Tests (Cases 1-10)

**Test Location:** `backend/tests/`

**Cases:**
1. **Query Encoding Validation** - Verify TF-IDF (1, 10000) & SPECTER (1, 768) shapes
2. **Cluster Selection Logic** - Verify top-3 clusters with descending scores
3. **Hybrid Scoring Calculation** - Verify 0.7×semantic + 0.3×tfidf = 0.87 ✓
4. **Result Deduplication** - Verify no duplicate paper IDs in output
5. **URL Identifier Extraction** - Extract paper ID from Semantic Scholar URLs
6. **Complete Local Recommendation Flow** - Full pipeline: encode → cluster → FAISS → score → rank
7. **Asynchronous Web Search** - Verify job transitions: pending → running → completed
8. **Paper Selection and Refinement** - Resolve arXiv ID & fetch related papers
9. **Model and Index Loading** - Load all artifacts in <30s
10. **Response Time Validation** - Median latency <500ms (achieved: 412ms)

**Run Backend Tests:**

```bash
# Option 1: Inside Docker (Recommended)
docker compose exec -T backend pytest tests/ -v --tb=short

# Option 2: Local (requires Python + dependencies)
cd backend
python3 -m pip install -r requirements.txt pytest httpx
python3 -m pytest tests/ -v

# Run with output saved to file
docker compose exec -T backend pytest tests/ -v | tee ../testing/evidence/pytest-backend-verbose.txt

# Run specific test
docker compose exec -T backend pytest tests/test_whitebox.py::test_query_encoding_validation -v

# Run with coverage
docker compose exec -T backend pytest tests/ --cov=. --cov-report=html
```

### Frontend Tests (Cases 11-14)

**Test Location:** `frontend/e2e/functional.spec.ts`

**Cases:**
11. **Valid Query Processing** - Section A shows local results (timing: ~1.2s)
12. **Empty Query Handling** - Displays validation error
13. **Special Characters** - Process "C++ programming" without crash
14. **Frontend-Backend Communication** - CORS headers validation

**Run Frontend Tests:**

```bash
# Install Playwright (one-time)
cd frontend
npm install
npx playwright install

# Run all tests
npm run test:e2e

# Run tests with UI (headed mode)
npm run test:e2e:headed

# Run specific test
npx playwright test functional.spec.ts -g "Case 11"

# Run with output saved
npm run test:e2e | tee ../testing/evidence/playwright-verbose.txt

# Generate HTML report
npx playwright show-report
```

### Evidence Artifacts

After running tests, evidence is saved to `testing/evidence/`:

```
testing/evidence/
├── pytest-backend-verbose.txt        # Full pytest output (10 passed)
├── playwright-verbose.txt             # Full Playwright output (4 passed)
├── junit-backend.xml                  # JUnit XML format
└── test-results/                      # Playwright HTML reports
```

**Use these files in your report as Appendix A (Backend) and Appendix B (Frontend).**

---

## 🔌 API Documentation

### Base URL
- **Docker:** `http://localhost:8000`
- **Local:** `http://localhost:8000`
- **Swagger UI:** `http://localhost:8000/docs`

### Key Endpoints

#### 1. Get Recommendations
**Endpoint:** `POST /api/recommend`

**Request:**
```json
{
  "query": "deep learning for computer vision",
  "top_k": 20,
  "web_top_k": 10
}
```

**Response:**
```json
{
  "status": "success",
  "sectionA": [
    {
      "source": "local",
      "paper_id": "abc123",
      "title": "Vision Transformer: An Image is Worth 16x16 Words",
      "year": 2020,
      "abstract": "...",
      "url": "https://arxiv.org/abs/2010.11929",
      "relevance_score": 0.92,
      "citations": 15000,
      "venue": "ICCV",
      "scopus_indexed": true
    }
  ],
  "web_job_id": "job-uuid"
}
```

#### 2. Get Local Results (Enriched)
**Endpoint:** `GET /api/recommend/local-enriched?query=machine+learning&top_k=20`

**Response:** Same format as above (local results with metadata)

#### 3. Refine Recommendations
**Endpoint:** `POST /api/refine`

**Request:**
```json
{
  "seed_paper_id": "arxiv:1706.03762",
  "web_top_k": 10
}
```

**Response:** Related papers from Semantic Scholar

#### 4. Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": true,
  "faiss_indices": 152,
  "response_time_ms": 45
}
```

---

## ⚙️ Configuration

### Backend Environment Variables

**Optional (.env file or docker-compose):**

```bash
# Hugging Face
HUGGINGFACE_HUB_TOKEN=hf_xxxxxxxxxxxx    # Optional: Higher rate limits

# Semantic Scholar
S2_API_KEY=your_api_key_here             # Optional: API key for S2

# PyTorch/Transformers
HF_HOME=/app/hf_cache                    # Cache directory
TRANSFORMERS_CACHE=/app/hf_cache        # Model cache (auto-set)

# Logging
PYTHONUNBUFFERED=1                       # Real-time logging (set in docker-compose)
```

### Frontend Configuration

**Vite Config (frontend/vite.config.js):**
- Development server: `http://localhost:5173`
- Build output: `dist/`
- Environment: `.env` file support

**Playwright Config (frontend/playwright.config.js):**
- Browser: Chromium (headless)
- Base URL: `http://localhost:5173`
- Timeout: 30 seconds
- Web server: Auto-start (configured)

---

## 🐛 Troubleshooting

### Backend Issues

**Issue: Models not loading / "ModuleNotFoundError"**
```bash
# Solution 1: Reinstall requirements in Docker
docker compose down -v
docker compose up --build

# Solution 2: Check volumes
docker volume ls
docker volume inspect be-project_hf_cache
```

**Issue: FAISS indices not found**
```bash
# Solution: Ensure artifacts folder exists
ls -la backend/artifacts/
# Should contain: *.faiss, *.pkl, *.npy files
```

**Issue: Port 8000 already in use**
```bash
# Solution: Use different port
docker compose up -d && docker-compose.yml:
# Change "8000:8000" to "8001:8000"
# Then: http://localhost:8001/docs
```

**Issue: Out of memory**
```bash
# Solution: Allocate more RAM to Docker
# Docker Desktop: Preferences → Resources → Memory (set to 6GB+)
```

### Frontend Issues

**Issue: "CORS error" when calling backend**
```bash
# Solution: Ensure backend is running
curl http://localhost:8000/health

# Check CORS whitelist in backend/app.py line 33-36
# Add your frontend URL if not present
```

**Issue: Playwright tests timeout**
```bash
# Solution: Increase timeout in playwright.config.js
# timeout: 30000 → 60000 (milliseconds)
```

**Issue: Node modules not found**
```bash
# Solution: Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Docker Issues

**Issue: Container exits immediately**
```bash
# Solution: Check logs
docker compose logs backend
docker compose logs frontend

# Rebuild
docker compose down -v && docker compose up --build
```

**Issue: Volume permissions denied**
```bash
# Solution (Linux/Mac): Fix ownership
sudo chown -R $USER:$USER backend/artifacts/
```

---

## 📊 Performance Benchmarks

| **Metric** | **Value** | **Target** |
|---|---|---|
| Local response time (p50) | 412ms | <500ms | ✅
| Local response time (p95) | ~650ms | <1000ms | ✅
| Queries per second (throughput) | ~2-3 QPS | >1 QPS | ✅
| Model load time | <30s | <30s | ✅
| Memory usage (backend) | ~2.5GB | <4GB | ✅
| Memory usage (frontend) | ~150MB | <500MB | ✅

---

## 📝 Development Workflow

### Making Changes

**Backend:**
1. Modify `backend/app.py` or `backend/local_recommender.py`
2. If running locally with `--reload`, changes auto-reload
3. If using Docker, rebuild: `docker compose up --build`

**Frontend:**
1. Modify `frontend/src/App.jsx` or styles
2. Vite auto-refreshes on `npm run dev`
3. In Docker, changes auto-reload via bind mount

**Tests:**
1. Add test cases to `backend/tests/` or `frontend/e2e/`
2. Run: `pytest tests/ -v` or `npm run test:e2e`

### Committing Code

```bash
# Check changes
git status

# Stage files
git add .

# Commit with message
git commit -m "Feat: Add refinement endpoint"

# Push to remote
git push origin main
```

---

## 📚 Additional Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/
- **Vite Guide:** https://vitejs.dev/guide/
- **Playwright Testing:** https://playwright.dev/
- **Docker Compose:** https://docs.docker.com/compose/
- **Semantic Scholar API:** https://www.semanticscholar.org/
- **FAISS Documentation:** https://github.com/facebookresearch/faiss/wiki

---

## 📄 Report Integration

### Attaching Test Evidence

For your project report Section 6 (Testing):

1. **Backend Tests (White-box + Integration):**
   - Attach: `testing/evidence/pytest-backend-verbose.txt`
   - Shows: All 10 test cases passing with timestamps

2. **Frontend Tests (Black-box):**
   - Attach: `testing/evidence/playwright-verbose.txt`
   - Shows: All 4 test cases passing with timings

3. **Performance Metrics:**
   - Include benchmark table from "Performance Benchmarks" section
   - Shows: Actual vs. target metrics

---

## 📧 Support & Contact

- **Project Repository:** [GitHub URL]
- **Issues:** Create GitHub issue with detailed description
- **Documentation:** See diagrams in `diagrams/` folder

---

## 📄 License

[Add appropriate license here]

---

**Last Updated:** June 2026
**Project Status:** ✅ Complete - All 14 test cases passing
