# Git LFS Setup & Push Guide

## Problem We're Solving

Large artifact files (114MB+ SBERT embeddings, 240MB+ FAISS indices) should NOT be stored in regular Git. Instead, they should be tracked with **Git Large File Storage (LFS)**.

When pushing without LFS:
- ❌ Regular Git stores full file contents (bloats repository)
- ❌ Cloning becomes slow (downloads full history of large files)
- ❌ GitHub rejects files >100MB on free tier

When pushing WITH LFS:
- ✅ Only pointers stored in Git (~130 bytes instead of 100MB+)
- ✅ Actual files stored on LFS server
- ✅ Clone is fast (only downloads what you need)
- ✅ Works with GitHub free tier

---

## Step-by-Step Setup

### 1. Install Git LFS (if not already installed)

**Mac:**
```bash
brew install git-lfs
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install git-lfs
```

**Windows:**
```bash
# Download from https://git-lfs.com
# Or use chocolatey:
choco install git-lfs
```

**Verify installation:**
```bash
git lfs version
# Should output: git-lfs/X.X.X
```

### 2. Initialize Git LFS in Your Repository

```bash
cd '/Users/Srirang.Kalantri/BE PROJECT CODE'

# Initialize LFS for this repo (one-time setup)
git lfs install

# Verify it's installed
git lfs version
```

### 3. Configure Which Files to Track with LFS

```bash
# Track all pickle files
git lfs track "*.pkl"

# Track numpy arrays
git lfs track "*.npy"

# Track FAISS indices
git lfs track "backend/artifacts/faiss_clusters/*.index"

# List what's being tracked
git lfs track

# This creates/updates .gitattributes
cat .gitattributes
```

**Expected .gitattributes output:**
```
*.pkl filter=lfs diff=lfs merge=lfs -text
*.npy filter=lfs diff=lfs merge=lfs -text
backend/artifacts/faiss_clusters/*.index filter=lfs diff=lfs merge=lfs -text
```

### 4. Add .gitattributes to Git

```bash
# Make sure .gitattributes is tracked
git add .gitattributes
git commit -m "chore: Configure Git LFS for large artifact files"
```

### 5. Migrate Already-Committed Large Files (If Needed)

If large files were already committed in Git history:

```bash
# This rewrites history to move files to LFS
git lfs migrate import --include="*.pkl,*.npy,backend/artifacts/faiss_clusters/*.index"

# Review changes
git log --oneline -5

# Push to remote
git push origin main --force  # ⚠️ Only if you're the only contributor
```

### 6. Stage Your Changes

```bash
# Add all modified files
git add .

# Verify what's staged
git status
```

**Expected output:**
```
Changes to be committed:
  modified:   README.md
  modified:   docker-compose.yml
  modified:   frontend/package-lock.json
  new file:   GIT_LFS_SETUP.md
  new file:   backend/tests/
  new file:   frontend/e2e/
  ...
  modified:   .gitattributes
```

### 7. Commit Your Changes

```bash
git commit -m "feat: Add comprehensive testing suite and update documentation

- Add 14 test cases (10 backend pytest + 4 frontend Playwright)
- Update README with full project documentation
- Fix docker-compose.yml (remove obsolete version field)
- Configure Git LFS for large artifact files
- Add testing, frontend, and backend improvements

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### 8. Push to GitHub

```bash
# Push to your remote repository
git push origin main

# Verify push completed
git log --oneline -1
```

---

## Verification

### Check Your GitHub Repository

1. **Navigate to your repo:** `https://github.com/yourusername/BE-project`

2. **Verify LFS files are pointers:**
   - Go to `backend/artifacts/tfidf_vectorizer.pkl`
   - Should show ~130 bytes with text like:
     ```
     version https://git-lfs.github.com/spec/v1
     oid sha256:...
     size 196000
     ```

3. **View LFS storage:** Settings → Code, storage & data

---

## For Collaborators (Cloning Your Repo)

When someone clones your repo, they need:

```bash
# Clone as normal (Git LFS auto-downloads)
git clone https://github.com/yourusername/BE-project.git
cd BE-project

# Install LFS (if not already done)
git lfs install

# Pull LFS files (usually automatic, but to be sure)
git lfs pull

# Verify artifacts are real files (not pointers)
file backend/artifacts/tfidf_vectorizer.pkl
# Should output: "data" (not "ASCII text")

# Start Docker
docker compose up --build
```

---

## Common Issues & Solutions

### Issue: Files are still LFS pointers after push

**Solution:**
```bash
# Verify LFS is configured
git lfs track

# If files weren't tracked, add them:
git lfs track "*.pkl" "*.npy"
git add .gitattributes
git commit -m "Configure LFS tracking"

# Remove from Git cache
git rm --cached backend/artifacts/*.pkl
git rm --cached backend/artifacts/*.npy
git rm --cached backend/artifacts/faiss_clusters/*.index

# Re-add and commit
git add backend/artifacts
git commit -m "Switch to LFS tracking"
git push origin main
```

### Issue: "Pointer file" warning when cloning

**Solution on client side:**
```bash
# Ensure LFS is installed
git lfs install

# Pull the actual files
git lfs pull

# Verify
file backend/artifacts/tfidf_vectorizer.pkl
```

### Issue: GitHub storage limit exceeded

**Solution:**
- Upgrade to GitHub Pro ($4/month) for more LFS storage
- Or use alternative: AWS S3, Google Cloud Storage, Hugging Face Hub
- Move models to Hugging Face Hub and download at startup

---

## Alternative: Store Models on Hugging Face Hub

For very large models (SPECTER, FAISS indices), consider:

```bash
# 1. Create Hugging Face account & repo
# 2. Upload models to Hugging Face:
from huggingface_hub import upload_folder

upload_folder(
    folder_path="backend/artifacts",
    repo_id="yourusername/be-project-artifacts",
    repo_type="dataset"
)

# 3. In your code, download at startup:
from huggingface_hub import hf_hub_download

tfidf = pickle.load(
    open(hf_hub_download("yourusername/be-project-artifacts", "tfidf_vectorizer.pkl"), "rb")
)
```

**Benefits:**
- ✅ Unlimited free storage
- ✅ CDN-backed downloads (fast globally)
- ✅ Models instantly accessible from any machine
- ✅ No Git repository bloat

---

## Quick Reference Commands

```bash
# Check LFS status
git lfs track

# See what will be pushed
git lfs ls-files

# Migrate existing files to LFS
git lfs migrate import --include="*.pkl,*.npy"

# Clone with LFS
git clone <repo-url>
git lfs pull

# Push normally (LFS files go to LFS server)
git push origin main
```

---

## For Your Current Setup

**Right now:**

```bash
cd '/Users/Srirang.Kalantri/BE PROJECT CODE'

# 1. Ensure Git LFS is installed
git lfs install

# 2. Configure LFS tracking
git lfs track "*.pkl" "*.npy"
git lfs track "backend/artifacts/faiss_clusters/*.index"

# 3. Add .gitattributes
git add .gitattributes

# 4. Stage all changes
git add .

# 5. Commit
git commit -m "feat: Add testing, documentation, and configure Git LFS"

# 6. Push
git push origin main
```

---

**Done!** ✅ Your project is now properly configured for GitHub with Git LFS.

Next developers who clone will automatically get the correct artifact files!
