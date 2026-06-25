# Module-Based System Architecture - Quick Guide

## What Changed?

### ❌ OLD (Tech Stack Focused)
- "React + Vite (Nginx:3000)"
- "FastAPI (Port 8000)"
- "TF-IDF (10K dim), SPECTER (768 dim)"
- "K-Means Clustering (152 clusters)"
- "FAISS Indexing (per-cluster)"
- Endpoint names: /recommend, /web-results, /refine

### ✅ NEW (Module Focused)
- "Query Interface", "Results Display", "Interaction Handler"
- "Query Orchestrator", "Local Retrieval Engine"
- "Feature Extraction Module", "Clustering Module"
- "Index Builder Module"
- "External Data Connector"
- Path labels: Path A (Sync), Path B (Async), Path C (Sync)

---

## Files Created

### 1. **system_architecture_modular.puml** (PlantUML - Component Diagram)
   - Full component-based diagram
   - Shows all tiers, modules, and data flows
   - Color-coded by layer
   - Includes legend and notes
   
   **To generate:**
   ```bash
   # Online
   Go to: https://www.plantuml.com/plantuml/uml/
   Copy content from system_architecture_modular.puml
   Paste and download PNG
   
   # Local (if you have PlantUML installed)
   plantuml system_architecture_modular.puml
   ```

### 2. **system_architecture_simple.puml** (PlantUML - Simplified)
   - Cleaner, more compact version
   - Block-based design (similar to reference images)
   - Easier to read
   - Same functionality shown
   
   **To generate:** Same as above

### 3. **DRAW_IO_INSTRUCTIONS_MODULAR.md** (Manual Drawing Guide)
   - Step-by-step instructions for Draw.io
   - Exact dimensions, colors, and layout
   - Matches reference image style
   - Takes 30-40 minutes to create
   
   **To use:**
   ```bash
   Go to: https://app.diagrams.net/
   Follow instructions in DRAW_IO_INSTRUCTIONS_MODULAR.md
   ```

### 4. **system_architecture_modular.md** (Conceptual Design Doc)
   - Explains the module-based approach
   - Lists all modules and their responsibilities
   - Shows data flow paths A/B/C
   - Good for understanding before drawing

---

## Recommended Approach

### Option 1: Quick (PlantUML - 5 minutes)
1. Open https://www.plantuml.com/plantuml/uml/
2. Copy content from `system_architecture_simple.puml`
3. Paste, download as PNG
4. Done!

**Best for:** Fast iteration, automatic layout

### Option 2: Custom (Draw.io - 30-40 minutes)
1. Open https://app.diagrams.net/
2. Follow `DRAW_IO_INSTRUCTIONS_MODULAR.md`
3. Manually arrange modules for perfect layout
4. Export as PNG

**Best for:** Exact control, custom styling, matching reference images perfectly

### Option 3: Hybrid (PlantUML first, then Draw.io)
1. Generate PlantUML diagram to see structure
2. Use it as reference for Draw.io
3. Recreate in Draw.io with custom layout

**Best for:** Getting ideas before manual work

---

## Key Design Principles

### 1. Technology Abstraction
- Use **"Query Interface"** not "React Component"
- Use **"Local Retrieval Engine"** not "TF-IDF + SPECTER + FAISS"
- Use **"Feature Extraction"** not "10K-dim vectors"

### 2. Functional Naming
- Focus on **what it does**, not **how it's implemented**
- Example: "Clustering Module" instead of "K-Means (152 clusters)"

### 3. Clear Hierarchy
- **Offline Pipeline** (top) → pre-processes corpus
- **Online Pipeline** (bottom) → handles queries
  - **Tier 1:** User interaction (Presentation)
  - **Tier 2:** Business logic (Application)
  - **Tier 3:** Data access (Data)

### 4. Data Flow Emphasis
- **Path A:** Local corpus search (synchronous)
- **Path B:** Web discovery (asynchronous)
- **Path C:** Interactive refinement (synchronous)

### 5. Visual Consistency
- **Colors:** Blue (Presentation), Green (Application), Yellow (Data), Orange (External)
- **Shapes:** Rectangles (modules), Cylinders (storage), Clouds (external)
- **Lines:** Solid (sync), Dashed (data population/reference)

---

## Comparison with Reference Images

### Reference Image 1 (Vertical Stack)
- ✅ Clean module stacking
- ✅ No tech stack visible
- ✅ Clear data flow arrows
- ✅ Legend included
- **Our design matches this style in `system_architecture_simple.puml`**

### Reference Image 2 (Complex Module Layout)
- ✅ Multiple interconnected modules
- ✅ Different module types (DB, processing, visualization)
- ✅ External connections
- ✅ Color-coded by function
- **Our design matches this style in `DRAW_IO_INSTRUCTIONS_MODULAR.md`**

---

## Testing Your Diagram

Before finalizing, check:

1. **No technology names visible?**
   - ❌ React, FastAPI, TF-IDF, SPECTER, FAISS, K-Means
   - ✅ Interface, Engine, Module, Connector

2. **No implementation details?**
   - ❌ Port numbers, dimensions, cluster counts
   - ✅ Sync/Async labels, Path A/B/C

3. **Clear module boundaries?**
   - ✅ Each box has a single responsibility
   - ✅ Tiers are visually separated

4. **Readable at presentation size?**
   - ✅ Font size ≥ 11pt
   - ✅ Colors have good contrast
   - ✅ Labels are concise

5. **Matches reference style?**
   - ✅ Similar shape usage
   - ✅ Similar color scheme
   - ✅ Similar level of abstraction

---

## Next Steps

1. **Choose your approach** (PlantUML quick or Draw.io custom)
2. **Generate the diagram**
3. **Save as `system_architecture.png`** in project root
4. **Update LaTeX** to reference new diagram
5. **Verify** it looks good in compiled PDF

---

## Support Files Reference

| File | Purpose | When to Use |
|------|---------|-------------|
| `system_architecture_modular.puml` | Full PlantUML component diagram | Want detailed automatic layout |
| `system_architecture_simple.puml` | Simplified PlantUML block diagram | Want quick, clean result |
| `DRAW_IO_INSTRUCTIONS_MODULAR.md` | Manual drawing guide | Want exact control, custom styling |
| `system_architecture_modular.md` | Conceptual design doc | Want to understand modules first |
| `DIAGRAM_SPECIFICATIONS.md` (updated) | Main specification | Reference for all diagrams |

---

## Questions?

**Q: Which file should I use?**
A: Start with `system_architecture_simple.puml` for PlantUML, or `DRAW_IO_INSTRUCTIONS_MODULAR.md` for Draw.io.

**Q: Can I still mention technologies in the paper?**
A: Yes! Describe implementation details in text/tables, but keep the architecture diagram abstract.

**Q: What if reviewers ask for more detail?**
A: You can add a separate "Implementation Details" table or appendix. The architecture diagram should stay high-level.

**Q: Should I remove ALL technical terms?**
A: Keep domain terms (e.g., "clustering", "indexing", "embedding") but remove specific library/framework names.

---

## Time Estimate

- **PlantUML (simple.puml):** 5 minutes
- **PlantUML (modular.puml):** 5 minutes
- **Draw.io (following guide):** 30-40 minutes
- **Draw.io (custom from scratch):** 60-90 minutes

**Recommendation:** Try PlantUML first to see if it meets your needs. If you want more control, use Draw.io.

---

Good luck! Your new architecture diagram will be much cleaner and more professional. 🎯
