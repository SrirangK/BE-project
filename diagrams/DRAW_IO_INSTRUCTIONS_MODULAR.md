# Draw.io Instructions for Module-Based System Architecture

## Style Reference
Based on your reference images, the new architecture should:
- Use **rounded rectangles** for modules/components
- Use **cylinders** only for databases/storage
- Use **cloud shapes** for external services
- **NO technology names** (no React, FastAPI, TF-IDF, SPECTER, FAISS, etc.)
- Use **functional names** for modules
- Keep it **clean and hierarchical**

---

## Layout Structure

### Canvas Settings
- **Size:** Custom 1920 x 1400 px (or A4 Landscape)
- **Zoom:** 100%
- **Grid:** Enabled (helps alignment)

---

## Step-by-Step Creation

### 1. OFFLINE PROCESSING PIPELINE (Top Section)

**Background Box:**
1. Insert → Rectangle (rounded corners: 10)
2. Size: Width 1800px, Height 200px
3. Fill: Light Gray (#F5F5F5)
4. Border: Dark Gray (#666666), 2px
5. Text: "OFFLINE PROCESSING PIPELINE" (centered, top, bold, 18pt)

**Inside the box, create horizontal flow:**

```
[Cylinder: Paper Corpus] → [Box: Data Ingestion] → [Box: Text Preprocessing] 
→ [Box: Feature Extraction] → [Box: Clustering Engine] → [Box: Index Builder]
```

**Components:**
- **Cylinder** (for Paper Corpus):
  - General → Cylinder
  - Fill: White
  - Border: Gray
  - Text: "Paper\nCorpus"

- **Rectangles** (rounded, 10px radius):
  - Fill: White (#FFFFFF)
  - Border: Gray (#666666), 1px
  - Size: ~150px x 80px each
  - Text (centered, 11pt):
    - "Data\nIngestion"
    - "Text\nPreprocessing"
    - "Feature\nExtraction"
    - "Clustering\nEngine"
    - "Index\nBuilder"

**Arrows:**
- Style: Solid line, arrow end
- Width: 2px
- Color: Black
- No labels needed (flow is obvious)

---

### 2. ONLINE PROCESSING PIPELINE (Bottom Section)

**Background Box:**
1. Rectangle (rounded corners: 10)
2. Size: Width 1800px, Height 900px
3. Fill: Very Light Gray (#FAFAFA)
4. Border: Dark Gray (#666666), 2px
5. Text: "ONLINE PROCESSING PIPELINE" (centered, top, bold, 18pt)

---

### 3. TIER 1: PRESENTATION LAYER

**Position:** Top-left inside online pipeline box

**Container:**
- Rectangle (rounded 10px)
- Size: ~350px x 250px
- Fill: Light Blue (#BBDEFB)
- Border: Blue (#1976D2), 2px
- Text: "PRESENTATION LAYER" (top-left corner, bold, 14pt)

**Components inside (3 boxes vertically stacked):**
- Rounded rectangles (~280px x 60px)
- Fill: White
- Border: Blue (#1976D2), 1px
- Spacing: 10px between boxes
- Text (centered, 11pt):
  - "Query Interface"
  - "Results Display"
  - "Interaction Handler"

---

### 4. TIER 2: APPLICATION LAYER

**Position:** Middle section of online pipeline

**Container:**
- Rectangle (rounded 10px)
- Size: ~800px x 250px
- Fill: Light Green (#C8E6C9)
- Border: Green (#388E3C), 2px
- Text: "APPLICATION LAYER" (top-left corner, bold, 14pt)

**Component 1: Query Orchestrator (left side):**
- Rounded rectangle (~200px x 200px)
- Fill: White
- Border: Green (#388E3C), 1px
- Text: "Query\nOrchestrator" (centered, 11pt)

**Component 2: Processing Paths (right side, 3 boxes):**
Create 3 rounded rectangles horizontally:
- Size: ~180px x 180px each
- Fill: White
- Border: Green (#388E3C), 1px
- Spacing: 10px between
- Text (centered, bold, 11pt):
  - "Local Retrieval\nEngine\n\n(Path A - Sync)"
  - "Web Discovery\nEngine\n\n(Path B - Async)"
  - "Refinement\nEngine\n\n(Path C - Sync)"

**Add small note inside each path box (smaller text, 9pt):**
- Path A: "Encoding • Clustering\nSearch • Ranking"
- Path B: "Job Queue • API\nPolling • Results"
- Path C: "ID Resolution\nRecommendations"

---

### 5. TIER 3: DATA LAYER

**Position:** Bottom section of online pipeline

**Container:**
- Rectangle (rounded 10px)
- Size: ~800px x 200px
- Fill: Light Yellow (#FFF9C4)
- Border: Orange (#F57F17), 2px
- Text: "DATA LAYER" (top-left corner, bold, 14pt)

**Components (3 items horizontally):**

1. **Offline Data Store** (Cylinder):
   - General → Cylinder
   - Size: ~180px x 140px
   - Fill: White
   - Border: Orange (#F57F17), 1px
   - Text: "Offline\nData Store"

2. **Job Queue** (Cylinder):
   - Same style
   - Text: "Job\nQueue"

3. **External Data Connector** (Rounded rectangle):
   - Size: ~180px x 140px
   - Fill: White
   - Border: Orange (#F57F17), 1px
   - Text: "External\nData\nConnector"

---

### 6. EXTERNAL SYSTEM (Right side)

**Position:** Right side of online pipeline, middle

**Component:**
- Cloud shape (General → Cloud)
- Size: ~300px x 200px
- Fill: Light Orange (#FFE0B2)
- Border: Deep Orange (#E64A19), 2px
- Text: "External Paper\nDatabase\n\n(e.g., Semantic Scholar,\nGoogle Scholar)"

---

### 7. USER/ACTOR (Left side)

**Position:** Far left, aligned with Presentation Layer

**Component:**
- Insert → Basic Shapes → Person icon (or stick figure)
- Size: ~80px x 120px
- Fill: Gray (#E0E0E0)
- Border: Dark Gray, 1px
- Text below: "Researcher"

---

### 8. CONNECTING ARROWS

**User to Presentation:**
- User → Query Interface: Label "Submit Query"
- Results Display → User: Label "View Results"
- User → Interaction Handler: Label "Refine"

**Presentation to Application:**
- Query Interface → Query Orchestrator (solid arrow)
- Query Orchestrator → Results Display (solid arrow)

**Application Internal:**
- Query Orchestrator → Local Retrieval Engine: Label "Path A"
- Query Orchestrator → Web Discovery Engine: Label "Path B"
- Query Orchestrator → Refinement Engine: Label "Path C"

**Application to Data:**
- Local Retrieval Engine → Offline Data Store (solid arrow)
- Web Discovery Engine → Job Queue (solid arrow)
- Web Discovery Engine → External Data Connector (solid arrow)
- Refinement Engine → External Data Connector (solid arrow)

**Data to External:**
- External Data Connector → External Paper Database (solid arrow, label: "API Calls")

**Offline to Online Connection:**
- Index Builder (offline) → Offline Data Store (data layer)
  - Use **dashed arrow** with label "Populate Indices"
  - This shows the connection between offline and online pipelines

---

### 9. DASHED BOX FOR PROCESSING PATHS (Optional Enhancement)

Draw a **dashed rectangle** around the three path boxes in Application Layer:
- No fill (transparent)
- Border: Dashed, Green (#388E3C), 1px
- Label above: "Processing Paths"

---

### 10. LEGEND (Bottom-right corner)

Create a small legend box:
- Rectangle (~250px x 150px)
- Fill: White
- Border: Black, 1px

**Legend items:**
```
━━━━→  Synchronous flow
- - - →  Data population / Reference
☁     External service
▭     Processing module
⬭     Data storage
```

Add small colored squares next to tier descriptions:
- 🟦 Presentation Layer
- 🟩 Application Layer  
- 🟨 Data Layer
- 🟧 External Systems

---

## Final Touches

### Color Summary
- **Offline Pipeline Background:** #F5F5F5
- **Presentation Layer:** #BBDEFB (border: #1976D2)
- **Application Layer:** #C8E6C9 (border: #388E3C)
- **Data Layer:** #FFF9C4 (border: #F57F17)
- **External Systems:** #FFE0B2 (border: #E64A19)
- **Components:** White fill (#FFFFFF)

### Typography
- **Section headers:** Bold, 14-18pt
- **Component names:** Regular, 11pt
- **Small notes:** Regular, 9pt
- **Arrow labels:** Regular, 9pt
- **Font:** Arial or Helvetica

### Spacing
- 20px margin from outer borders
- 10px spacing between components
- 30px spacing between tiers

---

## Export Settings

When done:
1. Select all (Ctrl+A / Cmd+A)
2. File → Export As → PNG
3. Settings:
   - **Zoom:** 100%
   - **Border Width:** 10px
   - **Transparent Background:** No
   - **Selection Only:** Yes (if you selected all)
4. **Save as:** `system_architecture.png`

---

## Key Differences from Old Diagram

### ❌ REMOVED (Tech Stack Details):
- React + Vite, Nginx:3000
- FastAPI, Port 8000
- Specific endpoints (/recommend, /web-results, etc.)
- TF-IDF (10K dim), SPECTER (768 dim)
- K-Means (152 clusters)
- FAISS details

### ✅ ADDED (Functional Focus):
- Generic module names
- Clear tier separation
- Path A/B/C labels
- Processing flow descriptions
- External system abstraction
- Clean, hierarchical layout

---

## Time Estimate
**30-40 minutes** for first-time creation
**15-20 minutes** if you've used Draw.io before

---

## Alternative: Simplified Version

If the above is too complex, create a **simplified 3-tier diagram** like reference image #2:

```
[User] → [Presentation] → [Application] → [Data] → [External]
           (3 modules)     (Orchestrator   (3 stores)  (Cloud)
                           + 3 engines)
```

This gives you a clean, module-based view without overwhelming detail.

Would you like me to provide the simplified version instructions instead?
