# Figure Types Guide - Coded vs Screenshots

## Current 4 Figures (All Should Be CODED/DIAGRAMS):

### ✅ **Figure 1: Methodology Flow** (`fig1_methodology.pdf`)
- **Type:** Coded Diagram (DOT → PDF)
- **Tool:** Graphviz DOT file
- **Why:** Flowchart showing process flow - best as coded diagram
- **File:** `fig1_methodology.dot` → convert to PDF

### ✅ **Figure 2: System Architecture** (`fig2_architecture.pdf`)
- **Type:** Coded Diagram (DOT → PDF)
- **Tool:** Graphviz DOT file
- **Why:** Architecture diagram with boxes and arrows - best as coded diagram
- **File:** `fig2_architecture.dot` → convert to PDF

### ✅ **Figure 3: Prefect Orchestration Flow** (`fig3_prefect_flow.pdf`)
- **Type:** Coded Diagram (DOT → PDF)
- **Tool:** Graphviz DOT file
- **Why:** Workflow flowchart - best as coded diagram
- **File:** `fig3_prefect_flow.dot` → convert to PDF

### ✅ **Figure 4: Model Performance + SHAP** (`fig6_model_comparison.pdf`)
- **Type:** Coded Chart (Python → PDF)
- **Tool:** Python (Matplotlib)
- **Why:** Data visualization charts - best as coded for reproducibility
- **File:** `create_fig6_combined.py` → run to generate PDF

---

## Summary:

**ALL 4 FIGURES = CODED/DIAGRAMS (No Screenshots Needed)**

- **Figures 1-3:** Use DOT files (already created) → convert to PDF
- **Figure 4:** Use Python script → generate PDF

**No screenshots required** - everything is generated programmatically, which is better for:
- Professional appearance
- Consistent styling
- Easy updates
- IEEE format compliance

---

## How to Generate All Figures:

### Step 1: Convert DOT files to PDF
```powershell
cd figures
.\convert_figures.ps1
```

This creates:
- `fig1_methodology.pdf`
- `fig2_architecture.pdf`
- `fig3_prefect_flow.pdf`

### Step 2: Generate Figure 4 (Python chart)
```powershell
cd figures
python create_fig6_combined.py
```

This creates:
- `fig6_model_comparison.pdf`

### Step 3: Verify all 4 PDFs exist
```powershell
ls *.pdf
```

Should show:
- fig1_methodology.pdf
- fig2_architecture.pdf
- fig3_prefect_flow.pdf
- fig6_model_comparison.pdf

---

## Why No Screenshots?

Screenshots are typically used for:
- UI demonstrations
- Software interfaces
- Real-world visualizations

But for academic papers, coded diagrams are preferred because:
1. **Professional:** Clean, consistent styling
2. **Scalable:** Vector graphics (PDF) scale perfectly
3. **Reproducible:** Can regenerate with updated data
4. **IEEE Compliant:** Black/white or grayscale friendly
5. **Easy to Edit:** Change labels/colors programmatically

Your dashboard screenshot was removed to save space, and the URL is mentioned in text instead.


