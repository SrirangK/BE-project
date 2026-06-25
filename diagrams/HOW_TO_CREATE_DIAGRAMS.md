# How to Create All 7 Diagrams - Step by Step Guide

## ✅ Quick Summary
You need to create 7 diagrams total:
1. **system_architecture.png** - Draw.io/PowerPoint (Complex, manual)
2. **use_case_diagram.png** - PlantUML (Auto-generated ✓)
3. **dfd_level0.png** - Draw.io (Simple)
4. **activity_diagram.png** - PlantUML (Auto-generated ✓)
5. **sequence_diagram.png** - PlantUML (Auto-generated ✓)
6. **functional_decomposition.png** - Draw.io/PowerPoint (Simple tree)
7. **pert_diagram.png** - Draw.io/PowerPoint (Simple flowchart)

---

## Method 1: PlantUML (3 diagrams - EASIEST!)

### For: Use Case, Sequence, Activity diagrams

**Steps:**
1. Go to: https://www.plantuml.com/plantuml/uml/
2. Copy content from the `.puml` files I created
3. Paste into the text editor
4. Click "Submit" or it auto-generates
5. Right-click on diagram → "Save image as..."
6. Save as PNG with exact names

**Files to use:**
- `diagrams/use_case_diagram.puml` → save as `use_case_diagram.png`
- `diagrams/sequence_diagram.puml` → save as `sequence_diagram.png`
- `diagrams/activity_diagram.puml` → save as `activity_diagram.png`

**That's 3/7 diagrams done in 5 minutes!** ✓

---

## Method 2: Draw.io (4 diagrams)

### Go to: https://app.diagrams.net/

---

### 1. System Architecture Diagram (Most Important!)

**Size:** Create blank diagram, A4 Landscape or Custom (1920x1200)

**Step-by-step:**

1. **Top Section - Offline Pipeline (Gray box):**
   ```
   - Insert → Rectangle (rounded)
   - Label: "OFFLINE PROCESSING PIPELINE"
   - Fill: Light Gray (#F5F5F5)
   - Inside, create flow: arXiv → Preprocessing → TF-IDF/SPECTER → K-Means → FAISS
   - Use arrows to connect
   ```

2. **Middle Section - Three Tiers:**
   
   **TIER 1 - Frontend (Blue):**
   - Rectangle with label "TIER 1: FRONTEND"
   - Fill: Light Blue (#E3F2FD)
   - Add inside: "React + Vite", "Nginx:3000", Components list
   
   **TIER 2 - Backend (Green):**
   - Rectangle with label "TIER 2: BACKEND"
   - Fill: Light Green (#E8F5E9)
   - Add inside: "FastAPI", "Port 8000", Endpoints list
   
   **TIER 3 - Data (Yellow):**
   - Rectangle with label "TIER 3: DATA LAYER"
   - Fill: Light Yellow (#FFF9C4)
   - Add inside: "Offline: TF-IDF, SPECTER, K-Means, FAISS", "Online: S2 API"

3. **Right Section - Data Flow Boxes:**
   
   Create 3 workflow boxes:
   - **Section A (Local):** Blue box with flow steps
   - **Section B (Web):** Orange box with async steps
   - **Section C (Refinement):** Purple box with refinement steps

4. **Connect with arrows:**
   - Frontend ↔ Backend (REST API)
   - Backend ↔ Data Layer
   - Backend → Workflow boxes

5. **Export:**
   - File → Export As → PNG
   - Zoom: 100%
   - Border Width: 10
   - **Save as: system_architecture.png**

**Time: 15-20 minutes**

---

### 2. DFD Level 0 (Simple!)

**Step-by-step:**

1. **Create External Entity (Researcher):**
   - Insert → Basic Shapes → Rectangle
   - Label: "Researcher"
   - Fill: Light Gray

2. **Create Process (Central System):**
   - Insert → Basic Shapes → Circle (or Rounded Rectangle)
   - Label: "Hybrid Paper\nRecommendation System"
   - Fill: Light Blue
   - Make it BIG (center of diagram)

3. **Create External Entity (S2 API):**
   - Insert → Rectangle
   - Label: "Semantic Scholar API"
   - Fill: Light Gray

4. **Create Data Flows (Arrows with labels):**
   - Researcher → System: "Query"
   - System → Researcher: "Recommendations"
   - System → S2 API: "API Request"
   - S2 API → System: "API Response"

5. **Optional - Add Data Stores (parallel lines):**
   - Create rectangles with open left side
   - Labels: "arXiv Corpus", "TF-IDF", "SPECTER", "FAISS", "Job Queue"
   - Connect to central system

6. **Export as: dfd_level0.png**

**Time: 10 minutes**

---

### 3. Functional Decomposition (Tree Diagram)

**Step-by-step:**

1. **Use SmartArt or manual tree:**
   - In Draw.io: Arrange → Insert → Layout → Tree
   - Or manually create with rectangles

2. **Level 0 (Top):**
   - Rectangle: "Hybrid Paper Recommendation System"

3. **Level 1 (4 boxes below):**
   - "Offline Processing"
   - "Query Processing"  
   - "Web Integration"
   - "User Interface"

4. **Level 2 (Components under each):**
   
   Under **Offline Processing:**
   - Data Loader
   - Text Preprocessor
   - TF-IDF Vectorizer
   - Semantic Encoder
   - Clustering Engine
   - Index Builder
   
   Under **Query Processing:**
   - Query Encoder
   - Cluster Selector
   - Candidate Retriever
   - Hybrid Scorer
   - Result Ranker
   
   Under **Web Integration:**
   - S2 API Client
   - Job Queue Manager
   - Identifier Resolver
   - Result Merger
   
   Under **User Interface:**
   - Query Input Component
   - Result Display Component
   - Selection Manager
   - Refinement Interface

5. **Color code by subsystem:**
   - Offline: Blue (#BBDEFB)
   - Query: Green (#C8E6C9)
   - Web: Orange (#FFE0B2)
   - UI: Purple (#E1BEE7)

6. **Export as: functional_decomposition.png**

**Time: 10 minutes**

---

### 4. PERT Diagram (Sequential Flow)

**Step-by-step:**

1. **Create Task Boxes (7 total):**
   - Insert → Rectangle (rounded)
   - Size: All same size
   
   For each task:
   ```
   ┌─────────────┐
   │     T1      │
   │  Literature │
   │   Survey    │
   │  (4 weeks)  │
   └─────────────┘
   ```

2. **Arrange vertically or left-to-right:**
   - T1 → T2 → T3 → T4 → T5 → T6 → T7

3. **Connect with THICK RED arrows:**
   - All connections are critical path
   - Add arrowheads

4. **Add cumulative timeline on side:**
   - Week 0, 4, 8, 11, 13, 15, 18, 20

5. **Add legend:**
   - "Critical Path (Slack = 0)"
   - "Total Duration: 20 weeks"

6. **Your tasks:**
   - T1: Literature Survey (4 weeks) [No dependency]
   - T2: Data Preprocessing (4 weeks) [Depends on T1]
   - T3: Feature Extraction (3 weeks) [Depends on T2]
   - T4: Clustering (2 weeks) [Depends on T3]
   - T5: Indexing (2 weeks) [Depends on T4]
   - T6: Recommendation Engine (3 weeks) [Depends on T5]
   - T7: Testing (2 weeks) [Depends on T6]

7. **Export as: pert_diagram.png**

**Time: 10 minutes**

---

## Alternative: PowerPoint/Google Slides

If you prefer PowerPoint:

1. **Use SmartArt for:**
   - Functional Decomposition (Hierarchy)
   - PERT (Process diagram)

2. **Use Shapes for:**
   - System Architecture (manually arrange)
   - DFD (circles + rectangles + arrows)

3. **Export each slide as PNG:**
   - File → Save As → PNG
   - Select "Current Slide Only"
   - Resolution: High (300 DPI)

---

## Final Checklist

Before submitting, verify each diagram has:

### All Diagrams:
- [ ] Clear, readable text (minimum 12pt font)
- [ ] Proper shapes for diagram type
- [ ] Consistent colors
- [ ] High resolution (at least 1200px wide)
- [ ] Saved as PNG format
- [ ] Named exactly as referenced in LaTeX

### Specific Checks:

**system_architecture.png:**
- [ ] Shows offline/online pipelines
- [ ] Shows all 3 tiers clearly
- [ ] Shows Sections A/B/C data flow
- [ ] Includes component names

**use_case_diagram.png:**
- [ ] Stick figure actors
- [ ] Oval use cases
- [ ] System boundary box
- [ ] Include/extend relationships shown

**dfd_level0.png:**
- [ ] External entities (rectangles)
- [ ] Central process (circle/rounded)
- [ ] Data stores (open rectangles)
- [ ] Labeled arrows

**activity_diagram.png:**
- [ ] Start/end nodes (circles)
- [ ] Activities (rounded rectangles)
- [ ] Decision diamonds
- [ ] Fork/join bars for parallel flows

**sequence_diagram.png:**
- [ ] Participants at top
- [ ] Lifelines (dashed vertical lines)
- [ ] Messages (horizontal arrows with labels)
- [ ] Activation boxes
- [ ] Sections A/B/C clearly separated

**functional_decomposition.png:**
- [ ] Hierarchical tree structure
- [ ] All 4 main subsystems
- [ ] Components listed under each
- [ ] Color coded

**pert_diagram.png:**
- [ ] All 7 tasks with durations
- [ ] Sequential flow with arrows
- [ ] Critical path highlighted
- [ ] Timeline shown

---

## Time Estimate

| Diagram | Tool | Estimated Time |
|---------|------|----------------|
| Use Case | PlantUML | 2 min (auto) |
| Sequence | PlantUML | 2 min (auto) |
| Activity | PlantUML | 2 min (auto) |
| DFD | Draw.io | 10 min |
| Functional | Draw.io | 10 min |
| PERT | Draw.io | 10 min |
| System Arch | Draw.io | 20 min |
| **TOTAL** | | **~1 hour** |

---

## Quick Links

- **PlantUML Online:** https://www.plantuml.com/plantuml/uml/
- **Draw.io Online:** https://app.diagrams.net/
- **Your .puml files:** Located in `BE PROJECT CODE/diagrams/` folder

---

## Tips

1. **For PlantUML diagrams:** Copy-paste the .puml file content directly, no editing needed
2. **For Draw.io:** Start with DFD and PERT (easiest), then Functional Decomposition, save System Architecture for last
3. **Keep it simple:** Don't over-design, clarity > beauty
4. **Use consistent colors** across all diagrams
5. **Test in LaTeX:** Place diagrams in project folder and compile to check sizing

---

## Need Help?

If any diagram doesn't look right:
1. Check the detailed specifications in `DIAGRAM_SPECIFICATIONS.md`
2. Verify you're using correct UML notation for each type
3. Make sure PNG resolution is high enough (zoom should be clear)
4. Text should be readable when printed on A4 paper

Good luck! You should be able to complete all 7 diagrams in about 1 hour. 🎯
