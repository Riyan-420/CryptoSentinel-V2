# Streamlit V2 Project - Complete Implementation Prompt

> **Quick Start:** This prompt provides complete instructions for building a Streamlit v2 that addresses ALL missing requirements. Use this when starting a new Cursor session to build the improved version.

## Project Overview
Build a **Streamlit-based ML prediction platform** that combines:
- **Current CryptoSentinel project** (Bitcoin price prediction) - Reference: `C:\Users\demon\Desktop\SEM 5\Machine Learning\Project\code-companion-hub`
- **Friend's AQI project** (Air Quality Index prediction) - Reference: [Provide path when available]
- **All missing critical requirements** (Feature Store, Model Registry, etc.)

## 📋 Quick Checklist - All Requirements

### ✅ Already Implemented (Keep)
- [x] Feature engineering pipeline
- [x] Multiple model training (XGBoost, RF, GBR, Ridge)
- [x] Model selection & evaluation
- [x] SHAP explainability
- [x] EDA & trend analysis
- [x] Alert system
- [x] Drift detection
- [x] CI/CD workflows (structure)

### ❌ Must Implement (Critical)
- [ ] **Feature Store Integration** (Hopsworks/Vertex AI)
- [ ] **Model Registry Integration** (Hopsworks/Vertex AI)
- [ ] **Training Pipeline - Fetch from Feature Store**
- [ ] **Streamlit App - Load from Model Registry**
- [ ] **Streamlit App - 6 pages with all features**
- [ ] **Update CI/CD workflows** (remove TODOs, add cloud integration)

## Core Requirements

### ✅ **What's Already Working (Keep These)**
1. **ML Pipeline Architecture**
   - Feature engineering (time-based + derived features)
   - Multiple model training (XGBoost, RandomForest, GradientBoosting, Ridge)
   - Model selection (best model based on RMSE/MAE/R²)
   - Prediction generation with confidence scores
   - SHAP explainability
   - EDA (trend identification, anomaly detection)
   - Alert system (price movement monitoring)
   - Drift detection (DeepChecks integration)
   - Market regime classification (K-Means clustering)

2. **Backend Structure** (from `backend/` folder)
   - `ml/pipeline/` - Data ingestion, feature engineering, flows
   - `ml/models/` - Trainer, predictor, registry, explainer
   - `api/` - FastAPI routes (can be adapted for Streamlit)
   - `core/config.py` - Configuration management

3. **CI/CD Workflows**
   - GitHub Actions for hourly feature pipeline
   - GitHub Actions for daily training pipeline
   - (Currently have TODO placeholders for Feature Store)

### ❌ **Critical Missing Requirements (MUST IMPLEMENT)**

#### 1. **Feature Store Integration (CRITICAL)**
**Current State:**
- Features computed on-the-fly in `ml/pipeline/feature_engineering.py`
- No persistent storage of features
- Training pipeline recomputes features every time

**Required Implementation:**
- **Choose: Hopsworks (recommended - free tier available) OR Vertex AI Feature Store**
- **Integration Points:**
  - After feature engineering in `ml/pipeline/feature_engineering.py`, store features in Feature Store
  - Modify `ml/pipeline/flows.py` to:
    - Store features after `engineer_features_task()`
    - Fetch historical features from Feature Store during training (instead of recomputing)
  - Create `ml/storage/feature_store.py` with:
    - `store_features(df: pd.DataFrame, timestamp: datetime)` - Store features
    - `fetch_features(start_date: datetime, end_date: datetime)` - Fetch historical features
    - `get_latest_features()` - Get most recent features for prediction

**Hopsworks Implementation Example:**
```python
# ml/storage/feature_store.py
import hopsworks
from datetime import datetime
import pandas as pd

class FeatureStoreManager:
    def __init__(self):
        self.project = hopsworks.login()
        self.fs = self.project.get_feature_store()
        self.feature_group = self.fs.get_or_create_feature_group(
            name="crypto_features",
            version=1,
            description="Cryptocurrency price prediction features"
        )
    
    def store_features(self, df: pd.DataFrame, timestamp: datetime):
        df['timestamp'] = timestamp
        self.feature_group.insert(df)
    
    def fetch_features(self, start_date: datetime, end_date: datetime):
        return self.feature_group.select_all().filter(
            (self.feature_group.timestamp >= start_date) &
            (self.feature_group.timestamp <= end_date)
        ).read()
```

**Update Workflows:**
- `.github/workflows/feature-pipeline-hourly.yml` - Remove TODO, add Feature Store storage
- `.github/workflows/training-pipeline-daily.yml` - Remove TODO, fetch from Feature Store

---

#### 2. **Model Registry Integration (CRITICAL)**
**Current State:**
- Models saved locally in `model_store/active/` and `model_store/saved/`
- Versioning handled by `ml/models/registry.py` (local JSON file)
- No cloud-based model registry

**Required Implementation:**
- **Choose: Hopsworks Model Registry (recommended) OR Vertex AI Model Registry**
- **Integration Points:**
  - Modify `ml/models/trainer.py`:
    - After `_save_models()`, also register model in cloud registry
    - Store model metadata (RMSE, MAE, R², training date, feature names)
  - Modify `ml/models/predictor.py`:
    - Load models from Model Registry (with fallback to local)
    - Check for model updates/versions
  - Create `ml/storage/model_registry.py` with:
    - `register_model(model_path: str, metrics: dict, version: str)` - Register trained model
    - `get_latest_model()` - Get best model from registry
    - `list_model_versions()` - List all model versions
    - `download_model(version: str)` - Download model for prediction

**Hopsworks Implementation Example:**
```python
# ml/storage/model_registry.py
import hopsworks
from ml.models.registry import get_model_metrics

class ModelRegistryManager:
    def __init__(self):
        self.project = hopsworks.login()
        self.mr = self.project.get_model_registry()
    
    def register_model(self, model_path: str, metrics: dict):
        model = self.mr.python.create_model(
            name="crypto_predictor",
            metrics=metrics,
            description=f"RMSE: {metrics['rmse']:.6f}, MAE: {metrics['mae']:.6f}"
        )
        model.save(model_path)
        return model
    
    def get_latest_model(self):
        model = self.mr.get_model("crypto_predictor", version=None)
        return model.download()
```

**Update Workflows:**
- `.github/workflows/training-pipeline-daily.yml` - Remove TODO, register model after training

---

#### 3. **Training Pipeline - Feature Store Integration (CRITICAL)**
**Current State:**
- `ml/pipeline/flows.py` -> `train_models_task()` computes features on-the-fly
- No historical feature retrieval

**Required Implementation:**
- Modify `ml/pipeline/flows.py`:
  - In `train_models_task()`, fetch historical features from Feature Store
  - Only compute new features for latest data
  - Combine historical + new features for training
  - Example:
    ```python
    @task(name="Train Models")
    def train_models_task(df: pd.DataFrame) -> Dict[str, Any]:
        from ml.storage.feature_store import FeatureStoreManager
        
        fs = FeatureStoreManager()
        # Fetch last 30 days of features from Feature Store
        historical_features = fs.fetch_features(
            start_date=datetime.now() - timedelta(days=30),
            end_date=datetime.now()
        )
        
        # Combine with new features
        combined_df = pd.concat([historical_features, df], ignore_index=True)
        
        trainer = ModelTrainer()
        metrics = trainer.train_all(combined_df)
        return metrics
    ```

---

#### 4. **Web App - Feature Store Integration (CRITICAL)**
**Current State:**
- Streamlit app loads models from local `model_store/active/`
- Features computed on-the-fly for predictions

**Required Implementation:**
- Modify Streamlit app (`app.py` or `dashboard.py`):
  - Load models from Model Registry (with local fallback)
  - Fetch latest features from Feature Store for predictions
  - Display model version and metadata from registry
  - Example:
    ```python
    # In Streamlit app
    from ml.storage.model_registry import ModelRegistryManager
    from ml.storage.feature_store import FeatureStoreManager
    
    @st.cache_resource
    def load_model():
        try:
            mr = ModelRegistryManager()
            model_path = mr.get_latest_model()
            return joblib.load(model_path)
        except:
            # Fallback to local
            return joblib.load("model_store/active/regressor.joblib")
    
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def get_latest_features():
        fs = FeatureStoreManager()
        return fs.get_latest_features()
    ```

---

## Streamlit App Structure

### **File Organization**
```
streamlit_v2/
├── app.py                          # Main Streamlit dashboard
├── pages/
│   ├── 1_🏠_Home.py                # Main dashboard (predictions, metrics)
│   ├── 2_📊_Predictions.py         # Detailed predictions & history
│   ├── 3_🔍_Explainability.py      # SHAP values, feature importance
│   ├── 4_📈_EDA.py                 # Exploratory data analysis
│   ├── 5_⚠️_Alerts.py              # Alert system
│   └── 6_⚙️_Pipeline.py           # Pipeline status, drift detection
├── backend/                        # Reuse existing backend (with modifications)
│   ├── ml/
│   │   ├── pipeline/              # Keep existing
│   │   ├── models/                # Keep existing
│   │   └── storage/               # NEW: Feature Store & Model Registry
│   │       ├── feature_store.py
│   │       └── model_registry.py
│   └── core/
├── requirements.txt                # Add: hopsworks, streamlit
└── .env                           # API keys: HOPSWORKS_API_KEY
```

### **Streamlit App Features**
1. **Home Page** (`pages/1_🏠_Home.py`)
   - Current price display
   - Latest prediction (price + direction)
   - Model metrics (RMSE, MAE, Accuracy)
   - Active model name from Model Registry
   - Quick stats (confidence, market regime)
   - Auto-refresh every 30 seconds

2. **Predictions Page** (`pages/2_📊_Predictions.py`)
   - Interactive price chart (Plotly)
   - Prediction history table
   - Validation status (correct/incorrect based on direction)
   - Prediction timeline

3. **Explainability Page** (`pages/3_🔍_Explainability.py`)
   - SHAP waterfall plot
   - Feature importance bar chart
   - Feature contribution table

4. **EDA Page** (`pages/4_📈_EDA.py`)
   - Trend analysis
   - Anomaly detection
   - Statistical summaries
   - Volatility charts

5. **Alerts Page** (`pages/5_⚠️_Alerts.py`)
   - Active alerts list
   - Critical alerts highlighted
   - Alert history
   - Alert configuration

6. **Pipeline Page** (`pages/6_⚙️_Pipeline.py`)
   - Pipeline status
   - Drift detection results
   - Last training time
   - Feature Store status
   - Model Registry status
   - Manual trigger buttons

---

## Implementation Checklist

### Phase 1: Feature Store Setup
- [ ] Sign up for Hopsworks (free tier) or Vertex AI
- [ ] Create `ml/storage/feature_store.py`
- [ ] Implement `store_features()` method
- [ ] Implement `fetch_features()` method
- [ ] Update `ml/pipeline/flows.py` to store features after engineering
- [ ] Update `ml/pipeline/flows.py` to fetch features during training
- [ ] Update `.github/workflows/feature-pipeline-hourly.yml` to store features
- [ ] Test feature storage and retrieval

### Phase 2: Model Registry Setup
- [ ] Create `ml/storage/model_registry.py`
- [ ] Implement `register_model()` method
- [ ] Implement `get_latest_model()` method
- [ ] Update `ml/models/trainer.py` to register models after training
- [ ] Update `ml/models/predictor.py` to load from registry (with local fallback)
- [ ] Update `.github/workflows/training-pipeline-daily.yml` to register models
- [ ] Test model registration and retrieval

### Phase 3: Streamlit App Development
- [ ] Create `app.py` with main layout
- [ ] Create `pages/1_🏠_Home.py` - Main dashboard
- [ ] Create `pages/2_📊_Predictions.py` - Predictions & history
- [ ] Create `pages/3_🔍_Explainability.py` - SHAP explainability
- [ ] Create `pages/4_📈_EDA.py` - Exploratory analysis
- [ ] Create `pages/5_⚠️_Alerts.py` - Alert system
- [ ] Create `pages/6_⚙️_Pipeline.py` - Pipeline monitoring
- [ ] Integrate Feature Store for feature retrieval
- [ ] Integrate Model Registry for model loading
- [ ] Add auto-refresh functionality
- [ ] Add error handling and fallbacks

### Phase 4: Testing & Validation
- [ ] Test Feature Store integration end-to-end
- [ ] Test Model Registry integration end-to-end
- [ ] Test Streamlit app with Feature Store models
- [ ] Test CI/CD workflows with cloud integrations
- [ ] Validate all requirements are met
- [ ] Performance testing (load times, refresh rates)

---

## Environment Variables Required

Create `.env` file:
```env
# Hopsworks (or Vertex AI)
HOPSWORKS_API_KEY=your_api_key_here
HOPSWORKS_PROJECT_NAME=your_project_name

# Or for Vertex AI:
# GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
# GCP_PROJECT_ID=your_project_id

# Existing configs
USE_GPU=true
OMP_NUM_THREADS=24
```

---

## Key Files to Reference

### From Current Project:
1. `backend/ml/pipeline/feature_engineering.py` - Feature computation logic
2. `backend/ml/pipeline/flows.py` - Pipeline orchestration
3. `backend/ml/models/trainer.py` - Model training logic
4. `backend/ml/models/predictor.py` - Prediction logic
5. `backend/ml/models/explainer.py` - SHAP explainability
6. `backend/ml/pipeline/eda.py` - EDA functions
7. `backend/ml/pipeline/alerts.py` - Alert system
8. `C:\Users\demon\Desktop\SEM 5\Machine Learning\Project\CryptoSentinel\CryptoSentinel\dashboard.py` - Existing Streamlit example

### From Friend's AQI Project:
- Reference their Feature Store implementation (if they have one)
- Reference their Streamlit structure
- Compare domain-specific feature engineering approaches

---

## Success Criteria

✅ **All Critical Requirements Met:**
1. Features stored in Feature Store (Hopsworks/Vertex AI)
2. Models registered in Model Registry (Hopsworks/Vertex AI)
3. Training pipeline fetches features from Feature Store
4. Streamlit app loads models from Model Registry
5. CI/CD workflows integrated with cloud services

✅ **All Existing Features Working:**
- Model training and selection
- Predictions with confidence
- SHAP explainability
- EDA and trend analysis
- Alert system
- Drift detection

✅ **Streamlit App Functional:**
- All 6 pages working
- Auto-refresh implemented
- Error handling with fallbacks
- Clean, professional UI

---

## Notes

- **Subscription Required:** Hopsworks free tier should be sufficient for development. For production, may need paid tier.
- **Fallback Strategy:** Always implement local fallback (current `model_store/`) in case cloud services are unavailable
- **Migration Path:** Keep existing local storage working while adding cloud integration
- **Testing:** Test both cloud and local fallback paths thoroughly

---

## Next Steps

1. Set up Hopsworks account (or Vertex AI)
2. Create `ml/storage/` directory structure
3. Implement Feature Store integration
4. Implement Model Registry integration
5. Build Streamlit app with all pages
6. Update CI/CD workflows
7. Test end-to-end
8. Deploy

---

**This prompt ensures all critical requirements are met while building a cleaner, simpler Streamlit-based version of the project.**

