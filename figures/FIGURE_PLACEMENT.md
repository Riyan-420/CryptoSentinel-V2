# Figure Placement Guide - 4 Figures Total

Since you only have space for 4 figures, here's the final layout:

## Final 4 Figures:

1. **Figure 1: Methodology Flow** (`fig1_methodology.pdf`)
   - Location: After "Complete Methodology Flow" section
   - Type: Flowchart (DOT → PDF)
   - Shows: 7-stage pipeline

2. **Figure 2: System Architecture** (`fig2_architecture.pdf`)
   - Location: After "System Architecture" section
   - Type: Architecture diagram (DOT → PDF)
   - Shows: All system components and data flow

3. **Figure 3: Prefect Orchestration Flow** (`fig3_prefect_flow.pdf`)
   - Location: After "Prefect Orchestration" section
   - Type: Flowchart (DOT → PDF)
   - Shows: Feature and Training pipelines
   - Note: CI/CD is described in text, referencing this figure

4. **Figure 4: Combined Model Performance + SHAP** (`fig6_model_comparison.pdf`)
   - Location: After "Model Explainability" section
   - Type: Combined chart (Python → PDF)
   - Shows: (a) Model comparison metrics, (b) SHAP waterfall
   - Use: `create_fig6_combined.py` script

## Removed Figures (described in text instead):

- **Containerization Workflow** - Described in text in Containerization section
- **CI/CD Pipeline** - Described in text, references Fig. 3
- **Dashboard Screenshot** - Optional, can be removed if space is tight

## To Create the Combined Figure 6:

```bash
cd figures
python create_fig6_combined.py
```

Make sure to replace the placeholder SHAP values with your actual SHAP data from your model!




