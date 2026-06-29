# Smart Pre-trained Research Paper Suggestion System

A hybrid recommendation system that combines local FAISS-based vector search with web-based Semantic Scholar recommendations to suggest relevant research papers.

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
# Health check: http://localhost:8000/health
```

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

## 🧪 Testing

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
