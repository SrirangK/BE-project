# ⚡ Quick Start (30 seconds)

## Just clone and run:

```bash
# Clone with Git LFS files
git clone https://github.com/yourusername/BE-project.git
cd BE-project

# Pull LFS files
git lfs pull

# Start Docker (takes 2-3 min on first run)
docker compose up --build

# Wait for output: "Uvicorn running on http://0.0.0.0:8000"

# Done! Access:
# Frontend: http://localhost:5173
# API Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

---

## Without Docker?

```bash
# Terminal 1 - Backend
cd backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn app:app --reload

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

---

## Run Tests

```bash
# Backend (10 tests)
docker compose exec -T backend pytest tests/ -v

# Frontend (4 tests)
cd frontend && npm run test:e2e
```

---

## Stop

```bash
docker compose down
```

---

**See `GETTING_STARTED.md` for full guide**
