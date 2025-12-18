# Figures Guide for CryptoSentinel IEEE Paper

This document provides detailed instructions for creating all 8 figures needed for the paper.

## Where to Create Figures

### Recommended Tools (Free & Easy):

1. **Draw.io (diagrams.net)** - BEST FOR FLOWCHARTS & ARCHITECTURE
   - Website: https://app.diagrams.net/ (free, no signup needed)
   - Export as PDF (vector format, perfect for LaTeX)
   - Easy to use, professional results

2. **Lucidchart** - Alternative to Draw.io
   - Website: https://www.lucidchart.com/
   - Free tier available

3. **Python (Matplotlib/Plotly)** - FOR CHARTS & GRAPHS
   - Use your existing codebase
   - Export as PDF or high-res PNG

4. **Screenshot Tools** - FOR DASHBOARD IMAGE
   - Windows: Snipping Tool or Win+Shift+S
   - macOS: Cmd+Shift+4
   - Ensure high resolution (at least 1920x1080)

---

## Figure 1: Complete Methodology Flow

**Location:** Section III (Methodology)

**How to Create (Draw.io):**
1. Go to https://app.diagrams.net/
2. Create new diagram
3. Add 7 rectangular boxes horizontally
4. Label each box:
   - "1. Data Collection\n(CoinGecko API)"
   - "2. Feature Engineering\n(40+ Indicators)"
   - "3. Feature Storage\n(Hopsworks)"
   - "4. Model Training\n(XGBoost, RF, GB, Ridge)"
   - "5. Model Evaluation\n(RMSE, MAE, R²)"
   - "6. Model Deployment\n(CI/CD to HF)"
   - "7. Real-Time Inference\n(FastAPI + Streamlit)"
5. Connect boxes with arrows (→)
6. Style: Rounded rectangles, blue outline, white fill
7. Export as PDF: File → Export as → PDF

**File:** Save as `figures/fig1_methodology.pdf`

---

## Figure 2: System Architecture

**Location:** Section III (Methodology)

**How to Create (Draw.io):**
1. Create layered architecture diagram
2. **Top Layer:** External Services
   - Box: "CoinGecko API"
   - Box: "Hopsworks Feature Store"
   - Box: "Hopsworks Model Registry"
3. **Second Layer:** Data Pipeline
   - Box: "Data Fetcher"
   - Box: "Feature Engineering"
4. **Third Layer:** ML API (Port 8000)
   - Box: "FastAPI Backend\n(Predictions, Validation)"
5. **Fourth Layer:** ML Models
   - Box: "XGBoost, RF, GB, Ridge"
   - Box: "Classifier, K-Means"
   - Box: "SHAP/LIME"
6. **Bottom Layer:** Frontend (Port 7860)
   - Box: "Streamlit Dashboard\n(8 Pages)"
7. **Side Layer:** Orchestration
   - Box: "Prefect Pipelines"
   - Box: "GitHub Actions"
8. **Container:** Draw large box around everything labeled "Docker Container\n(Hugging Face Spaces)"
9. Add arrows showing data flow
10. Export as PDF

**File:** Save as `figures/fig2_architecture.pdf`

---

## Figure 3: Prefect Orchestration Flow

**Location:** Section IV (Implementation), after "Prefect Orchestration"

**How to Create (Draw.io) - Based on your friend's style:**

### Part (a): Feature Pipeline (Left side, Blue background box)

1. Create a titled box: "feature_pipeline.py"
2. Inside, add:
   - **Prefect Features:** List (Automatic logging, Retries, Error handling)
   - **Start:** "@flow feature_pipeline()"
   - **Task 1:** "@task fetch_price_data()"
     - "Fetches 24h data from CoinGecko API"
     - "Retries: 3x, 30s delay"
   - **Task 2:** "@task engineer_features_task()"
     - "Computes 40+ technical indicators"
     - "RSI, MACD, Bollinger Bands, etc."
   - **Task 3:** "@task store_features_task()"
     - "Uploads to Hopsworks Feature Store"
     - "crypto_features, version 1"
     - "Automatic deduplication"
3. Arrow pointing out to "Hopsworks Feature Store"
4. Style: Blue background, white text

### Part (b): Training Pipeline (Right side, Green background box)

1. Create a titled box: "training_pipeline.py"
2. **Input:** Arrow from "Hopsworks Feature Store"
3. Inside, add:
   - **Start:** "@flow training_pipeline()"
   - **Task 1:** "@task load_features()"
     - "Loads from Hopsworks Feature Store"
   - **Task 2:** "@task check_drift_task()"
     - "DeepChecks drift detection"
   - **Task 3:** "@task train_models_task()"
     - "Trains all models"
   - **Task 4:** "@task select_best_model_task()"
     - "Selects based on validation RMSE"
   - **Task 5:** "@task save_models_task()"
     - "Saves models (.joblib)"
     - "Promotes best to active"
   - **Task 6:** "@task register_models_task()"
     - "Uploads to Hopsworks Model Registry"
4. Arrow pointing out to "Hopsworks Model Registry"
5. Style: Green background, white text

**Layout:** Place (a) and (b) side-by-side or stacked vertically
**File:** Save as `figures/fig3_prefect_flow.pdf`

---

## Figure 4: Containerization Workflow

**Location:** Section IV (Implementation), after "Containerization"

**How to Create (Draw.io) - Based on your friend's style:**

### Docker Image Section (Top):

1. Create large box: "Docker Image (Dockerfile)"
2. Inside, create layers:
   - **Base Layer:** "python:3.11-slim (~150 MB)"
   - **System Dependencies:** "build-essential, curl, git"
   - **Python Dependencies:** List:
     - "scikit-learn, XGBoost"
     - "SHAP, LIME, DeepChecks"
     - "Prefect, FastAPI, Streamlit"
     - "Hopsworks (requirements.txt)"
   - **Application Code:** 
     - "app/ (config.py, predictor.py, etc.)"
     - "pages/ (home.py, predictions.py, etc.)"
     - "pipelines/ (feature_pipeline.py, etc.)"
     - "storage/ (feature_store.py, model_registry.py)"
     - "dashboard.py"
     - "models/ (*.joblib)"
3. **Port Mapping:** "Port 7860 (Streamlit)"

### Container Runtime Section (Bottom):

1. Create box: "Container Runtime"
2. Inside:
   - **Main Process:** "Streamlit Dashboard"
     - Command: "streamlit run dashboard.py --server.port 7860"
     - "Background Scheduler: Feature & Training Pipelines"
   - **User Access:** Arrow from "User (Browser)" to "Port 7860"

**File:** Save as `figures/fig4_containerization.pdf`

---

## Figure 5: CI/CD Pipeline

**Location:** Section IV (Implementation), after "CI/CD Pipeline"

**How to Create (Draw.io):**

1. Create horizontal flowchart
2. Boxes in sequence:
   - "Code Push to GitHub"
   - "GitHub Actions Triggered"
   - Branch to 3 paths:
     - "Test Job\n(Linting, Import Tests)"
     - "Feature Pipeline Job\n(Every 5 min)"
     - "Training Pipeline Job\n(Every 30 min)"
   - "Deploy Job\n(On push to main)"
   - "Upload to Hugging Face Spaces"
   - "Docker Image Rebuild"
   - "Services Start Automatically"
3. Connect with arrows
4. Add labels for triggers (cron schedules)

**File:** Save as `figures/fig5_cicd_pipeline.pdf`

---

## Figure 6: Model Performance Comparison

**Location:** Section V (ML Experiments)

**How to Create (Python - Use your actual data):**

```python
import matplotlib.pyplot as plt
import numpy as np

# Replace with your actual metrics
models = ['XGBoost', 'Random Forest', 'Gradient Boosting', 'Ridge']
rmse = [245.32, 267.18, 271.45, 412.56]  # Your actual RMSE values
mae = [189.45, 201.23, 205.67, 328.91]   # Your actual MAE values
r2 = [0.892, 0.875, 0.869, 0.698]        # Your actual R² values

fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4))

# RMSE Bar Chart
ax1.bar(models, rmse, color=['#22c55e', '#6366f1', '#6366f1', '#ef4444'])
ax1.set_ylabel('RMSE')
ax1.set_title('RMSE Comparison')
ax1.tick_params(axis='x', rotation=45)

# MAE Bar Chart
ax2.bar(models, mae, color=['#22c55e', '#6366f1', '#6366f1', '#ef4444'])
ax2.set_ylabel('MAE')
ax2.set_title('MAE Comparison')
ax2.tick_params(axis='x', rotation=45)

# R² Bar Chart
ax3.bar(models, r2, color=['#22c55e', '#6366f1', '#6366f1', '#ef4444'])
ax3.set_ylabel('R² Score')
ax3.set_title('R² Comparison')
ax3.tick_params(axis='x', rotation=45)

plt.tight_layout()
plt.savefig('figures/fig6_model_comparison.pdf', dpi=300, bbox_inches='tight')
```

**File:** Save as `figures/fig6_model_comparison.pdf`

---

## Figure 7: SHAP Waterfall Plot

**Location:** Section V (ML Experiments)

**How to Create (Python - Use your actual SHAP data):**

```python
import shap
import matplotlib.pyplot as plt
import pandas as pd

# Use your actual model and features
# This is a template - replace with your actual code

# Assuming you have shap_values and feature_names
# shap_values = your_shap_values
# feature_names = your_feature_names

# Create waterfall plot
shap.plots.waterfall(shap_values[0], show=False)
plt.title('SHAP Waterfall Plot: Feature Contributions to Prediction')
plt.tight_layout()
plt.savefig('figures/fig7_shap_waterfall.pdf', dpi=300, bbox_inches='tight')
```

**Alternative:** If waterfall doesn't work, use bar chart:
```python
# Top 10 features by absolute SHAP value
top_features = sorted(zip(feature_names, shap_values[0]), 
                     key=lambda x: abs(x[1]), reverse=True)[:10]
features, values = zip(*top_features)

plt.figure(figsize=(8, 6))
colors = ['#22c55e' if v > 0 else '#ef4444' for v in values]
plt.barh(features, values, color=colors)
plt.xlabel('SHAP Value')
plt.title('Top 10 Feature Contributions (SHAP)')
plt.tight_layout()
plt.savefig('figures/fig7_shap_waterfall.pdf', dpi=300, bbox_inches='tight')
```

**File:** Save as `figures/fig7_shap_waterfall.pdf`

---

## Figure 8: Streamlit Dashboard Screenshot

**Location:** Section IV (Implementation), after "Frontend Dashboard"

**How to Create:**
1. Run your Streamlit app: `streamlit run dashboard.py`
2. Navigate to the main Dashboard page
3. Take a screenshot:
   - **Windows:** Win+Shift+S (Snipping Tool) or Print Screen
   - **macOS:** Cmd+Shift+4, then drag to select area
   - **Linux:** Use screenshot tool
4. Ensure screenshot shows:
   - Price chart with predictions
   - Current prediction display
   - Model metrics
   - Navigation sidebar
5. Crop to show only the dashboard (remove browser UI)
6. Save as high-resolution PNG (at least 1920x1080)

**File:** Save as `figures/fig8_dashboard_screenshot.png`

---

## Quick Start Guide

### Step 1: Create Figures Folder
```bash
mkdir figures
```

### Step 2: Create Figures in Order
1. **Figures 1-5:** Use Draw.io (https://app.diagrams.net/)
   - Create each figure
   - Export as PDF
   - Save to `figures/` folder

2. **Figures 6-7:** Use Python
   - Run the Python scripts above with your actual data
   - Save to `figures/` folder

3. **Figure 8:** Take screenshot
   - Run Streamlit app
   - Take screenshot
   - Save to `figures/` folder

### Step 3: Verify All Figures Exist
```bash
# Check all files are present
ls figures/
# Should show:
# fig1_methodology.pdf
# fig2_architecture.pdf
# fig3_prefect_flow.pdf
# fig4_containerization.pdf
# fig5_cicd_pipeline.pdf
# fig6_model_comparison.pdf
# fig7_shap_waterfall.pdf
# fig8_dashboard_screenshot.png
```

---

## Tips for Professional Figures

1. **Consistent Styling:**
   - Use same font (Arial or Helvetica) across all figures
   - Use consistent colors (blue for data flow, green for training, etc.)
   - Keep box sizes similar

2. **IEEE Format Requirements:**
   - Black and white or grayscale preferred
   - Text must be readable at column width
   - Minimum 300 DPI resolution

3. **Draw.io Tips:**
   - Use "Format" panel to style boxes
   - Use "Arrange" → "Layout" for automatic alignment
   - Use "Insert" → "Advanced" → "From Template" for IEEE-style templates

4. **Python Plotting Tips:**
   - Use `plt.style.use('seaborn-v0_8-whitegrid')` for clean plots
   - Set `dpi=300` when saving
   - Use `bbox_inches='tight'` to avoid clipping

---

## Troubleshooting

**Figure not showing in PDF?**
- Check file path: `figures/fig1_methodology.pdf` (relative to .tex file)
- Ensure file exists and is not corrupted
- Try compiling with `pdflatex` multiple times

**Figure too large/small?**
- Adjust `width=\columnwidth` to `width=0.8\columnwidth` for smaller
- Or use `width=0.5\columnwidth` for half-width figures

**Low quality?**
- Ensure PDFs are vector format (not rasterized)
- For PNG, use at least 300 DPI
- Check export settings in Draw.io

---

## Need Help?

- **Draw.io Tutorial:** https://www.diagrams.net/doc/
- **Matplotlib Docs:** https://matplotlib.org/stable/contents.html
- **SHAP Docs:** https://shap.readthedocs.io/
