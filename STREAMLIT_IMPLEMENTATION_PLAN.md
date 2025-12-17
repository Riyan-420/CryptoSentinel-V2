# CryptoSentinel - Streamlit Implementation

## Project Status: COMPLETE

This document outlines the implementation of CryptoSentinel, a Bitcoin price prediction system with ML.

---

## Project Structure

```
CryptoSentinel(streamlit)/
├── .github/
│   └── workflows/
│       ├── feature-pipeline.yml    # Runs every 30 min
│       └── training-pipeline.yml   # Runs every 30 min (offset)
├── .streamlit/
│   └── config.toml                 # Theme and server config
├── api/
│   ├── __init__.py
│   ├── main.py                     # FastAPI entry point
│   └── routes.py                   # All API endpoints
├── app/
│   ├── __init__.py
│   ├── config.py                   # Settings and paths
│   ├── data_fetcher.py             # CoinGecko API integration
│   ├── feature_engineering.py      # Technical indicators
│   ├── model_trainer.py            # Multi-model training
│   ├── predictor.py                # Prediction generation (FIXED)
│   ├── explainer.py                # SHAP and importance
│   ├── drift_detection.py          # DeepChecks/KS-test
│   ├── alerts.py                   # Alert system
│   └── eda.py                      # EDA utilities
├── pages/
│   ├── __init__.py
│   ├── dashboard.py                # Main dashboard
│   ├── predictions.py              # Prediction history
│   ├── model_insights.py           # SHAP/Importance
│   ├── data_analysis.py            # EDA and drift
│   ├── alerts_page.py              # Alert management
│   ├── pipeline_control.py         # Pipeline controls
│   └── about.py                    # Project info
├── pipelines/
│   ├── __init__.py
│   ├── feature_pipeline.py         # Data + feature engineering
│   ├── training_pipeline.py        # Model training
│   └── inference_pipeline.py       # Predictions
├── storage/
│   ├── __init__.py
│   ├── feature_store.py            # Hopsworks Feature Store
│   └── model_registry.py           # Hopsworks Model Registry
├── models/
│   ├── active/                     # Current serving models
│   └── saved/                      # Version history
├── data/                           # Local feature cache
├── dashboard.py                    # Streamlit entry point
├── requirements.txt                # Python 3.11.9 compatible
├── Dockerfile                      # Container definition
├── docker-compose.yml              # Multi-service orchestration
├── env.example                     # Environment template
└── .gitignore                      # Git exclusions
```

---

## Key Features Implemented

### 1. ML Models
- **XGBoost Regressor** (Primary)
- **Random Forest Regressor**
- **Gradient Boosting Regressor**
- **Ridge Regression**
- **Gradient Boosting Classifier** (Direction)
- **K-Means + PCA** (Market Regime)

### 2. Feature Engineering
- RSI, MACD, Bollinger Bands
- Moving Averages (SMA, EMA - 5, 10, 20)
- Volatility, Momentum, ROC
- Lag features, Time features

### 3. Hopsworks Integration
- Feature Store for centralized features
- Model Registry for versioning
- Local fallback for offline development

### 4. CI/CD Pipelines (GitHub Actions)
- Feature pipeline: `*/30 * * * *` (every 30 min)
- Training pipeline: `15,45 * * * *` (every 30 min, offset)

### 5. Prediction Validation (FIXED)
```python
# Tolerance-based validation prevents false positives
DIRECTION_TOLERANCE_PCT = 0.1  # 0.1%

# If price moves less than tolerance = neutral (incorrect)
# Otherwise, validate direction match
```

### 6. Beautiful Streamlit UI
- Dark theme with purple accents
- 7 distinct pages
- Explanatory dropdowns
- Interactive charts (Plotly)

---

## Quick Start

### Local Development
```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run Streamlit dashboard
streamlit run dashboard.py

# Run FastAPI backend (separate terminal)
python -m api.main
```

### Docker
```bash
# Build and run all services
docker-compose up -d

# Access Streamlit: http://localhost:8501
# Access API: http://localhost:8000
```

### Deployment
1. Set up Hopsworks account and get API key
2. Add secrets to GitHub:
   - `HOPSWORKS_API_KEY`
   - `HOPSWORKS_PROJECT_NAME`
3. Push to GitHub - workflows will run automatically
4. Deploy to Streamlit Cloud:
   - Connect GitHub repo
   - Set secrets in Streamlit Cloud settings

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/price/current | Current BTC price |
| GET | /api/price/history | Price history |
| GET | /api/prediction/current | Current prediction |
| GET | /api/prediction/history | Prediction history |
| GET | /api/prediction/accuracy | Accuracy stats |
| GET | /api/model/metrics | Model metrics |
| GET | /api/model/shap | SHAP values |
| GET | /api/model/importance | Feature importance |
| GET | /api/analysis/trend | Market trend |
| GET | /api/analysis/eda | EDA report |
| GET | /api/drift/reports | Drift reports |
| GET | /api/alerts | Alert history |
| POST | /api/pipeline/feature | Run feature pipeline |
| POST | /api/pipeline/training | Run training pipeline |
| POST | /api/pipeline/inference | Run inference pipeline |

---

## Configuration

Environment variables (set in `.env` or Streamlit secrets):

```
HOPSWORKS_API_KEY=your_key
HOPSWORKS_PROJECT_NAME=CryptoSentinel
TRAINING_INTERVAL_MINUTES=30
PREDICTION_REFRESH_MINUTES=5
DIRECTION_TOLERANCE_PCT=0.1
```

---

## Python Version

**Python 3.11.9** - All dependencies verified compatible.

