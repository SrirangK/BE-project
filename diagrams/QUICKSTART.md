# QUICKSTART: Generate Your New Architecture Diagram in 5 Minutes

## The Fastest Way (PlantUML Online)

### Step 1: Open PlantUML Editor
Go to: **https://www.plantuml.com/plantuml/uml/**

### Step 2: Copy the Code
Open this file in your project:
```
diagrams/system_architecture_simple.puml
```

Copy ALL the content (Ctrl+A / Cmd+A, then Ctrl+C / Cmd+C)

### Step 3: Paste & Generate
1. Paste into the PlantUML online editor (left panel)
2. It will automatically generate the diagram (right panel)
3. Wait 2-3 seconds for rendering

### Step 4: Download
1. Right-click on the diagram
2. Select "Save image as..."
3. Save as: `system_architecture.png`
4. Move it to your project folder

### Step 5: Use in LaTeX
```latex
\begin{figure}[h]
\centering
\includegraphics[width=\textwidth]{system_architecture.png}
\caption{System Architecture}
\label{fig:system_architecture}
\end{figure}
```

**Done! Total time: 5 minutes** ⏱️

---

## If You Want More Control (Draw.io - 30 minutes)

### Step 1: Open Draw.io
Go to: **https://app.diagrams.net/**

### Step 2: Follow the Guide
Open this file in your project:
```
diagrams/DRAW_IO_INSTRUCTIONS_MODULAR.md
```

Follow step-by-step instructions to create:
- Offline Pipeline (top section)
- Online Pipeline with 3 tiers
- Processing paths (A/B/C)
- External systems
- User actor

### Step 3: Export
1. File → Export As → PNG
2. Zoom: 100%
3. Border Width: 10px
4. Save as: `system_architecture.png`

**Done! Total time: 30-40 minutes** ⏱️

---

## Comparison: Which Method?

| Method | Time | Control | Best For |
|--------|------|---------|----------|
| **PlantUML (simple.puml)** | 5 min | Low | Quick iteration, automatic layout |
| **PlantUML (modular.puml)** | 5 min | Low | More detailed, still automatic |
| **Draw.io (guided)** | 30 min | High | Exact layout, custom styling |
| **Draw.io (from scratch)** | 60 min | Total | Complete customization |

**Recommendation:** Start with PlantUML. If you don't like the layout, use Draw.io.

---

## PlantUML: Simple vs. Modular

### `system_architecture_simple.puml`
- ✅ Cleaner layout
- ✅ Easier to read
- ✅ Better for presentations
- ✅ Matches reference image style
- **Use this for your report!**

### `system_architecture_modular.puml`
- More detailed
- Shows all connections
- Includes notes
- Better for technical documentation

---

## Common Issues & Fixes

### Issue 1: PlantUML diagram looks squashed
**Solution:** Adjust the package sizes in the .puml file, or use the simple version

### Issue 2: Text is too small
**Solution:** In the .puml file, change:
```plantuml
skinparam defaultFontSize 11
```
to:
```plantuml
skinparam defaultFontSize 13
```

### Issue 3: Colors don't match reference
**Solution:** Edit the color definitions at the top of the .puml file:
```plantuml
!define PRESENTATION_COLOR #BBDEFB
!define APPLICATION_COLOR #C8E6C9
!define DATA_COLOR #FFF9C4
```

### Issue 4: Want landscape orientation
**PlantUML:** Automatically landscape if you use `left to right direction`
**Draw.io:** Set canvas to 1920x1200 (landscape)

### Issue 5: Arrows crossing each other
**PlantUML:** Try adding `left to right direction` or `-down->` / `-right->` to force direction
**Draw.io:** Manually reroute arrows

---

## Files You Need

### For PlantUML:
1. `system_architecture_simple.puml` ← **Start here!**
2. `system_architecture_modular.puml` (alternative)

### For Draw.io:
1. `DRAW_IO_INSTRUCTIONS_MODULAR.md` ← **Follow this guide**

### For Understanding:
1. `README_MODULAR_ARCHITECTURE.md` (overview)
2. `BEFORE_AFTER_COMPARISON.md` (what changed)
3. `system_architecture_modular.md` (module descriptions)

---

## Verification Checklist

After generating your diagram, check:

### Content
- [ ] Shows offline pipeline (top)
- [ ] Shows online pipeline with 3 tiers
- [ ] Shows user/researcher actor
- [ ] Shows external database (cloud)
- [ ] Shows data flow arrows
- [ ] Shows Path A/B/C labels

### Style
- [ ] No tech stack names (React, FastAPI, etc.)
- [ ] No implementation details (port numbers, dimensions)
- [ ] Module names are generic and functional
- [ ] Colors match: Blue (presentation), Green (application), Yellow (data)
- [ ] Legend included
- [ ] Text is readable (≥ 11pt)

### Quality
- [ ] High resolution (≥ 1200px wide)
- [ ] PNG format
- [ ] Looks professional
- [ ] Matches reference image style

---

## What to Do Next

1. ✅ Generate diagram (PlantUML or Draw.io)
2. ✅ Save as `system_architecture.png`
3. ✅ Place in your LaTeX project folder
4. ✅ Update `\includegraphics` in your .tex file
5. ✅ Compile and verify it looks good
6. ✅ Update caption if needed

---

## Help & Support

### PlantUML Documentation
- Official site: https://plantuml.com/
- Component diagrams: https://plantuml.com/component-diagram
- Deployment diagrams: https://plantuml.com/deployment-diagram

### Draw.io Documentation
- Official site: https://www.diagrams.net/
- Tutorial: https://www.diagrams.net/doc/
- Examples: https://www.diagrams.net/example-diagrams

### Your Project Files
- Main spec: `DIAGRAM_SPECIFICATIONS.md` (updated Section 1)
- Overview: `README_MODULAR_ARCHITECTURE.md`
- Comparison: `BEFORE_AFTER_COMPARISON.md`
- Draw.io guide: `DRAW_IO_INSTRUCTIONS_MODULAR.md`

---

## Final Tip

**Start simple, iterate if needed.**

Don't spend hours perfecting the diagram on first try. Generate a quick version with PlantUML, see how it looks in your paper, then decide if you need more customization.

**Good luck!** 🚀

---

## TL;DR (Too Long; Didn't Read)

```bash
# Open browser
https://www.plantuml.com/plantuml/uml/

# Copy content from
diagrams/system_architecture_simple.puml

# Paste in PlantUML editor
# Download PNG
# Save as: system_architecture.png

# Done! ✅
```

**5 minutes. That's it.**
