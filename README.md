---
title: CryptoSentinel V2
emoji: 💰
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
license: mit
---

# CryptoSentinel - Bitcoin Price Prediction

Streamlit-based ML system for Bitcoin price prediction with automated drift detection and model retraining.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `env.example` to `.env` and add your Hopsworks API key:
```bash
HOPSWORKS_API_KEY=your_key_here
HOPSWORKS_PROJECT_NAME=CryptoSentinel
```

### 3. Run Everything (One Command)
```bash
python run_all.py
```

This runs:
- Feature pipeline (fetch data, engineer features)
- Training pipeline (train models, check drift)
- Inference pipeline (generate predictions)

### 4. Launch Dashboard
```bash
streamlit run dashboard.py
```

Or using venv:
```bash
.\venv\Scripts\streamlit.exe run dashboard.py
```

Access at: `http://localhost:8501`

---

## Features

### ML Models
- **4 Regression Models**: XGBoost, Random Forest, Gradient Boosting, Ridge
- **Auto-selects best** based on RMSE
- Direction classifier (up/down)
- K-Means clustering for market regimes

### Data Drift Detection
- Compares new data against training baseline
- DeepChecks + KS-test fallback
- Triggers retraining when drift detected
- Threshold: 0.3 (30%)

### Prediction System
- Every 5 minutes: New prediction
- After 30 minutes: Validation with 0.1% tolerance
- Tracks accuracy (last 20 validated predictions)
- Direction-based (not exact price)

### Dashboard Pages
1. **Dashboard** - Overview & current prediction
2. **Predictions** - History & accuracy tracking
3. **Model Insights** - SHAP & feature importance
4. **Data Analysis** - EDA & correlations
5. **Data Drift** - Drift monitoring & status
6. **Alerts** - Price change & volatility alerts
7. **Pipeline Control** - Manual pipeline triggers
8. **About** - System information

---

## Individual Pipeline Commands

**Feature Pipeline** (fetch + engineer):
```bash
python -m pipelines.feature_pipeline
```

**Training Pipeline** (train + drift check):
```bash
python -m pipelines.training_pipeline
```

**Inference Pipeline** (predict + validate):
```bash
python -m pipelines.inference_pipeline
```

---

## Optional: FastAPI Backend

For automated predictions every 5 minutes:

```bash
python -m api.main
```

Access at: `http://localhost:8000`

API Docs: `http://localhost:8000/docs`

---

## Configuration (`env.example`)

```
HOPSWORKS_API_KEY=your_api_key
HOPSWORKS_PROJECT_NAME=CryptoSentinel
TRAINING_INTERVAL_MINUTES=30
PREDICTION_REFRESH_MINUTES=5
DIRECTION_TOLERANCE_PCT=0.1
```

---

## Deployment

### Docker
```bash
docker-compose up -d
```

### GitHub Actions
Push to GitHub - workflows run automatically:
- Feature pipeline: Every 30 min
- Training pipeline: Every 30 min (offset)

Add secrets to GitHub:
- `HOPSWORKS_API_KEY`
- `HOPSWORKS_PROJECT_NAME`

### Streamlit Cloud
1. Connect GitHub repo
2. Add secrets in Streamlit settings
3. Deploy!

---

## Directory Structure

```
CryptoSentinel(streamlit)/
├── app/                    # Core ML modules
├── api/                    # FastAPI backend
├── pages/                  # Streamlit pages
├── pipelines/              # Prefect workflows
├── storage/                # Hopsworks integration
├── models/                 # Saved models
├── dashboard.py            # Streamlit entry
├── run_all.py              # One-command execution
└── requirements.txt        # Dependencies
```

---

## Key Concepts

### Prediction Accuracy
- Predicts direction (up/down) for next 30 minutes
- Validated after 30 minutes with 0.1% tolerance
- Sideways movement (<0.1%) = incorrect
- Tracks last 20 validated predictions

### Data Drift
- Baseline set during training
- Next run compares new data vs baseline
- Drift score >0.3 triggers retraining
- Ensures model stays current

### Model Selection
- Trains 4 regression models
- Selects best based on validation RMSE
- All models saved for comparison

---

## Python Version

**Python 3.11.9** (verified compatible)

---

## Support

For issues, check:
- Terminal output for errors
- Streamlit page error messages
- API logs at `http://localhost:8000/health`

