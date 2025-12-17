# CryptoSentinel - COMPREHENSIVE MUST-HAVES CHECKLIST

> **Purpose:** This document captures EVERY requirement from the course documents, cross-referenced with STREAMLIT_V2_PROMPT.md, to ensure NOTHING is missed.

---

## 🚨 CRITICAL FINDINGS FROM COURSE DOCUMENTS

### ⚠️ MAJOR REQUIREMENT NOT IN STREAMLIT_V2_PROMPT:

**The course REQUIRES FastAPI, not just Streamlit!**

From Screenshot 1: *"Design and Deploy an End-to-End Machine Learning System with **FastAPI**, CI/CD, Prefect, Automated Testing, and Docker Containerization"*

From Screenshot 2: *"Build and Deploy ML Models with **FastAPI** - Serve real-time model predictions using **FastAPI**"*

**This means we need BOTH:**
1. **FastAPI Backend** - For API endpoints, model serving, real-time predictions
2. **Streamlit Frontend** - For the dashboard/visualization

---

## 📋 MASTER REQUIREMENTS CHECKLIST

### 1. BUILD AND DEPLOY ML MODELS WITH FASTAPI 🔴 NOT IMPLEMENTED

| Requirement | Status | Notes |
|-------------|--------|-------|
| Train ML model (regression, classification, or deep learning) | ✅ Done | XGBoost, RF, GBR, Ridge, GBClassifier |
| Serve real-time predictions using **FastAPI** | ✅ Done | code-companion-hub has this |
| Implement endpoints handling different input types (JSON, file uploads, numeric features) | ⚠️ Partial | Only JSON currently |
| Efficient model loading | ✅ Done | joblib loading |
| Logging | ⚠️ Partial | Basic print statements, need proper logging |
| Maintainable code structure | ✅ Done | Modular structure |

**ACTION NEEDED:** Keep FastAPI backend, add proper logging, consider file upload endpoint

---

### 2. IMPLEMENT CI/CD PIPELINE USING GITHUB ACTIONS 🔴 INCOMPLETE

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Automate Code Checks** | ❌ Missing | Need linting (flake8/black), type checking |
| **Unit Tests** | ⚠️ Basic | tests/ folder exists but needs more |
| **ML Tests** | ❌ Missing | Need model performance tests |
| **Data Validation** | ❌ Missing | Need data schema validation |
| **Model Training Triggers** | ❌ Missing | Need workflow to trigger training |
| **Container Image Building** | ❌ Missing | Need docker build in CI |
| **Deployment Pipeline** | ❌ Missing | Need deployment to Streamlit Cloud/etc |
| Enable continuous integration | ❌ Missing | No workflows exist yet |
| Enable continuous delivery | ❌ Missing | No deployment automation |

**ACTION NEEDED:** Create complete GitHub Actions workflows:
1. `ci.yml` - Code checks, linting, tests
2. `feature-pipeline.yml` - Run every 30 min
3. `training-pipeline.yml` - Run every 30 min  
4. `docker-build.yml` - Build and push images
5. `deploy.yml` - Deploy to Streamlit Cloud

---

### 3. ORCHESTRATE ML WORKFLOWS USING PREFECT ✅ PARTIAL

| Requirement | Status | Notes |
|-------------|--------|-------|
| Data ingestion | ✅ Done | fetch_data_task() |
| Feature engineering | ✅ Done | engineer_features_task() |
| Model training | ✅ Done | train_models_task() |
| Evaluation | ✅ Done | Metrics computed |
| Saving and versioning the model | ✅ Done | model_store/saved/ |
| **Error handling** | ⚠️ Basic | Try/except exists |
| **Retry logic** | ❌ Missing | No Prefect retries configured |
| **Success/failure notifications (Discord/Email/Slack)** | ❌ Missing | REQUIRED! |

**ACTION NEEDED:** 
- Add `@task(retries=3, retry_delay_seconds=60)` to tasks
- Implement Discord/Slack webhook notifications
- Add proper error handling with alerts

---

### 4. IMPLEMENT AUTOMATED TESTING FOR ML MODELS 🔴 INCOMPLETE

| Requirement | Status | Notes |
|-------------|--------|-------|
| **Using DeepChecks or equivalent** | ✅ Done | drift_detection.py has DeepChecks |
| Test data integrity | ⚠️ Partial | check_data_quality() exists |
| **Identify drift** | ✅ Done | detect_drift() implemented |
| Validate performance metrics | ❌ Missing | No automated metric validation |
| **Detect issues during CI/CD automatically** | ❌ Missing | Not integrated into CI |

**ACTION NEEDED:**
- Create `tests/test_ml_models.py` with performance threshold tests
- Integrate DeepChecks into CI/CD pipeline
- Add automated alerts when drift > threshold

---

### 5. CONTAINERIZE THE ENTIRE SYSTEM ⚠️ PARTIAL

| Requirement | Status | Notes |
|-------------|--------|-------|
| Create Dockerfile for FastAPI service | ✅ Done | backend/Dockerfile |
| **Build and optimize the image** | ❌ Missing | No multi-stage builds, not optimized |
| **Run all services in containers** | ⚠️ Partial | docker-compose exists |
| Docker Compose (API + Prefect + database) | ⚠️ Partial | Has API + frontend, no Prefect |

**ACTION NEEDED:**
- Optimize Dockerfile with multi-stage builds
- Add Prefect worker to docker-compose
- Add Streamlit container
- Create production-ready compose file

---

### 6. ML EXPERIMENTATION & OBSERVATIONS ✅ DONE (needs documentation)

| Requirement | Status | Notes |
|-------------|--------|-------|
| Run multiple ML experiments | ✅ Done | 4 regression models compared |
| Log results (accuracy, RMSE, F1-score) | ✅ Done | Metrics tracked |
| Compare model versions (baseline vs improved) | ✅ Done | model_registry.json |
| Observations on best-performing model | ⚠️ Need doc | Need to document |
| Data quality issues | ⚠️ Need doc | Need to document |
| Overfitting/underfitting patterns | ⚠️ Need doc | Need to document |
| Deployment speed improvements with CI/CD | ❌ Missing | Need to implement & measure |
| Reliability improvements via Prefect | ❌ Missing | Need to implement & document |

**ACTION NEEDED:** Document all observations in project report

---

### 7. FEATURE STORE INTEGRATION (HOPSWORKS) 🔴 NOT IMPLEMENTED

| Requirement | Status | Notes |
|-------------|--------|-------|
| Store features after engineering | ❌ Missing | CRITICAL |
| Fetch historical features for training | ❌ Missing | CRITICAL |
| Retrieve latest features for predictions | ❌ Missing | CRITICAL |
| Backfill historical data | ❌ Missing | Need backfill script |

**ACTION NEEDED:** Implement `storage/feature_store.py` with Hopsworks integration

---

### 8. MODEL REGISTRY INTEGRATION (HOPSWORKS) 🔴 NOT IMPLEMENTED

| Requirement | Status | Notes |
|-------------|--------|-------|
| Register models after training | ❌ Missing | CRITICAL |
| Version control and metadata | ⚠️ Local only | model_registry.json is local |
| Load models from registry | ❌ Missing | CRITICAL |
| Streamlit app loads from Model Registry | ❌ Missing | CRITICAL |

**ACTION NEEDED:** Implement `storage/model_registry.py` with Hopsworks integration

---

### 9. MULTIPLE ML TASKS (RED TEXT - CRITICAL) ✅ DONE

| Task | Status | Implementation |
|------|--------|----------------|
| **Classification** | ✅ Done | Price direction (up/down) - GradientBoostingClassifier |
| **Regression** | ✅ Done | Price prediction - XGBoost, RF, GBR, Ridge |
| **Dimensionality Reduction** | ✅ Done | PCA |
| **Clustering** | ✅ Done | K-Means (market regime) |
| Time series analysis | ⚠️ Implicit | Technical indicators are time-series features |
| Recommendation systems | ❌ N/A | Not applicable to crypto prediction |
| Association | ❌ N/A | Not applicable |

**STATUS:** ✅ We have 4+ ML tasks which satisfies the requirement

---

### 10. WEB APP REQUIREMENTS

| Requirement | Status | Notes |
|-------------|--------|-------|
| Load model from Feature Store/Model Registry | ❌ Missing | Need Hopsworks |
| Load features from Feature Store | ❌ Missing | Need Hopsworks |
| Compute model predictions | ✅ Done | predictor.py |
| Show on simple and descriptive dashboard | ✅ Done | React frontend exists |
| **Perform EDA to identify trends** | ✅ Done | eda.py |
| **Variety of forecasting models** | ✅ Done | 4 regression models |
| **SHAP or LIME for feature importance** | ✅ Done | explainer.py |
| **Add alerts for hazardous levels** | ✅ Done | alerts.py |

---

### 11. DELIVERABLES CHECKLIST

#### 1. Source Code Repository (GitHub) ⚠️ PARTIAL

| Component | Status |
|-----------|--------|
| FastAPI app | ✅ Done |
| Prefect workflow | ✅ Done |
| Dockerfile + docker-compose | ✅ Done |
| ML model training scripts | ✅ Done |
| Automated tests | ⚠️ Basic |
| GitHub Actions workflow file | ❌ Missing |

#### 2. Demonstration Video (5-10 minutes) ❌ NOT DONE

Must show:
- [ ] Running API
- [ ] CI/CD workflow in action
- [ ] Prefect flow execution
- [ ] Dockerized services

#### 3. Project Report ❌ NOT DONE

Must include:
- [ ] Introduction, problem statement
- [ ] ML experiments & comparison
- [ ] System architecture diagram
- [ ] Containerization workflow
- [ ] CI/CD pipeline explanation
- [ ] Prefect orchestration flow
- [ ] Complete methodology flow diagram
- [ ] Final observations, limitations, and future work

---

## 🎯 PRIORITY ACTION ITEMS

### P0 - CRITICAL (Must Have for Passing)

1. **Hopsworks Feature Store Integration**
   - Create `storage/feature_store.py`
   - Store features after engineering
   - Fetch features for training
   - Get latest features for predictions

2. **Hopsworks Model Registry Integration**
   - Create `storage/model_registry.py`
   - Register models after training
   - Load models for predictions

3. **GitHub Actions CI/CD**
   - Create `.github/workflows/ci.yml`
   - Create `.github/workflows/feature-pipeline.yml`
   - Create `.github/workflows/training-pipeline.yml`
   - Include code checks, tests, docker build

4. **Prefect Notifications**
   - Add Discord/Slack webhook integration
   - Send notifications on success/failure

5. **Fix Prediction History Validation**
   - Add tolerance/headroom for direction validation

### P1 - HIGH (Important for Good Grade)

6. **Backfill Script**
   - Create script to backfill historical features
   - Store in Feature Store

7. **Docker Optimization**
   - Multi-stage Dockerfile
   - Add Streamlit container
   - Production docker-compose

8. **Automated ML Testing in CI**
   - DeepChecks in CI pipeline
   - Performance threshold tests

9. **Proper Logging**
   - Replace print() with logging
   - Add structured logs

### P2 - MEDIUM (Polish)

10. **File Upload Endpoint** (FastAPI can handle different input types)

11. **Retry Logic in Prefect**
    - Add retries to all tasks

12. **Project Documentation**
    - Architecture diagrams
    - API documentation

### P3 - DOCUMENTATION (Required for Submission)

13. **Project Report**
14. **Demo Video**

---

## 📊 ARCHITECTURE DIAGRAM (Required)

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GITHUB ACTIONS CI/CD                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ Code Checks  │  │   ML Tests   │  │ Docker Build │               │
│  │   (lint)     │  │ (DeepChecks) │  │   & Push     │               │
│  └──────────────┘  └──────────────┘  └──────────────┘               │
│         │                │                   │                       │
│         └────────────────┼───────────────────┘                       │
│                          │                                           │
│  ┌───────────────────────▼───────────────────────┐                  │
│  │          PREFECT ORCHESTRATION                 │                  │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐       │                  │
│  │  │ Feature │──│Training │──│Inference│       │                  │
│  │  │ Pipeline│  │Pipeline │  │Pipeline │       │                  │
│  │  └────┬────┘  └────┬────┘  └────┬────┘       │                  │
│  │       │            │            │             │                  │
│  │       │     Discord/Slack Notifications      │                  │
│  └───────┼────────────┼────────────┼────────────┘                  │
└──────────┼────────────┼────────────┼────────────────────────────────┘
           │            │            │
           ▼            ▼            ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         HOPSWORKS                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────┐           │
│  │     FEATURE STORE       │  │     MODEL REGISTRY      │           │
│  │  ┌─────────────────┐   │  │  ┌─────────────────┐    │           │
│  │  │ crypto_features │   │  │  │ crypto_predictor │    │           │
│  │  │ - price         │   │  │  │ - regressor.pkl  │    │           │
│  │  │ - returns       │   │  │  │ - classifier.pkl │    │           │
│  │  │ - rsi           │   │  │  │ - metrics.json   │    │           │
│  │  │ - macd          │   │  │  │ - version: v1.2  │    │           │
│  │  │ - volatility    │   │  │  └─────────────────┘    │           │
│  │  │ - ...           │   │  │                         │           │
│  │  └─────────────────┘   │  │                         │           │
│  └─────────────────────────┘  └─────────────────────────┘           │
└──────────────────────────────────────────────────────────────────────┘
           │                              │
           │                              │
           ▼                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                         DOCKER CONTAINERS                             │
│  ┌─────────────────────┐  ┌─────────────────────┐                    │
│  │    FASTAPI BACKEND  │  │ STREAMLIT FRONTEND  │                    │
│  │  ┌───────────────┐  │  │  ┌───────────────┐  │                    │
│  │  │ /api/predict  │  │  │  │   Dashboard   │  │                    │
│  │  │ /api/price    │  │  │  │   Predictions │  │                    │
│  │  │ /api/model    │  │  │  │   History     │  │                    │
│  │  │ /api/drift    │  │  │  │   SHAP/LIME   │  │                    │
│  │  │ /api/alerts   │  │  │  │   Drift       │  │                    │
│  │  └───────────────┘  │  │  │   Pipeline    │  │                    │
│  │  Port: 8000         │  │  │               │  │                    │
│  └─────────────────────┘  │  └───────────────┘  │                    │
│                           │  Port: 8501         │                    │
│                           └─────────────────────┘                    │
└──────────────────────────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────┐
│   COINGECKO API  │
│  (Data Source)   │
└──────────────────┘
```

---

## 📁 FINAL DIRECTORY STRUCTURE

```
CryptoSentinel-Streamlit/
├── .github/
│   └── workflows/
│       ├── ci.yml                      # Code checks, linting, tests
│       ├── feature-pipeline.yml        # Every 30 min - store features
│       ├── training-pipeline.yml       # Every 30 min - train & register
│       ├── docker-build.yml            # Build & push Docker images
│       └── deploy.yml                  # Deploy to Streamlit Cloud
│
├── .streamlit/
│   └── config.toml                     # Streamlit theme config
│
├── backend/                            # FastAPI Backend (REQUIRED!)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                     # FastAPI app entry
│   │   └── routes.py                   # API endpoints
│   ├── ml/
│   │   ├── pipeline/
│   │   │   ├── data_ingestion.py
│   │   │   ├── feature_engineering.py
│   │   │   ├── drift_detection.py
│   │   │   ├── eda.py
│   │   │   └── alerts.py
│   │   └── models/
│   │       ├── trainer.py
│   │       ├── predictor.py            # FIXED validation!
│   │       └── explainer.py
│   ├── core/
│   │   └── config.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── pipelines/                          # Prefect Flows
│   ├── __init__.py
│   ├── feature_pipeline.py             # Data → Features → Feature Store
│   ├── training_pipeline.py            # Feature Store → Train → Model Registry
│   ├── inference_pipeline.py           # Feature Store + Model Registry → Predict
│   └── notifications.py                # Discord/Slack webhooks
│
├── storage/                            # Hopsworks Integration
│   ├── __init__.py
│   ├── feature_store.py                # Hopsworks Feature Store
│   └── model_registry.py               # Hopsworks Model Registry
│
├── streamlit_app/                      # Streamlit Frontend
│   ├── app.py                          # Main entry point
│   ├── pages/
│   │   ├── 1_📊_Dashboard.py
│   │   ├── 2_📈_Price_Predictions.py
│   │   ├── 3_📜_Prediction_History.py
│   │   ├── 4_🧠_Model_Explainability.py
│   │   ├── 5_📊_Market_Regime.py
│   │   ├── 6_📉_Data_Drift.py
│   │   └── 7_⚙️_Pipeline.py
│   └── components/
│       ├── charts.py
│       ├── metrics.py
│       └── styles.py
│
├── tests/                              # Automated Tests
│   ├── __init__.py
│   ├── test_api.py                     # FastAPI endpoint tests
│   ├── test_ml_pipeline.py             # Pipeline tests
│   ├── test_models.py                  # Model performance tests
│   ├── test_feature_store.py           # Hopsworks tests
│   └── test_data_quality.py            # DeepChecks tests
│
├── scripts/
│   └── backfill.py                     # Backfill historical features
│
├── models/                             # Local fallback storage
│   ├── active/
│   └── saved/
│
├── docker-compose.yml                  # Full stack orchestration
├── docker-compose.prod.yml             # Production config
├── Dockerfile.backend                  # FastAPI container
├── Dockerfile.streamlit                # Streamlit container
├── requirements.txt                    # Combined dependencies
├── .env.example
├── .gitignore
├── README.md
└── docs/
    ├── ARCHITECTURE.md
    ├── API_DOCUMENTATION.md
    └── SETUP_GUIDE.md
```

---

## 🔍 CROSS-REFERENCE WITH STREAMLIT_V2_PROMPT.md

| Item in STREAMLIT_V2_PROMPT | Status | This Document |
|-----------------------------|--------|---------------|
| Feature Store Integration | ❌ Must Implement | ✅ Covered in P0 |
| Model Registry Integration | ❌ Must Implement | ✅ Covered in P0 |
| Training Pipeline - Fetch from Feature Store | ❌ Must Implement | ✅ Covered in P0 |
| Streamlit App - Load from Model Registry | ❌ Must Implement | ✅ Covered in P0 |
| Streamlit App - 6 pages | ❌ Must Implement | ✅ Now 7 pages |
| Update CI/CD workflows | ❌ Must Implement | ✅ 5 workflows defined |

---

## ⏰ TIMELINE ESTIMATE

| Phase | Duration | Tasks |
|-------|----------|-------|
| Phase 1 | Day 1 AM | Setup Git, structure, configs |
| Phase 2 | Day 1 PM | Hopsworks Feature Store + Model Registry |
| Phase 3 | Day 2 AM | Update Prefect pipelines with Hopsworks |
| Phase 4 | Day 2 PM | GitHub Actions CI/CD workflows |
| Phase 5 | Day 3 AM | Streamlit pages (adapt from React) |
| Phase 6 | Day 3 PM | Docker optimization, testing |
| Phase 7 | Day 4 | Documentation, demo video |

---

**Document Created:** 2025-01-17
**Last Updated:** 2025-01-17
**Status:** Ready for Implementation

> **IMPORTANT:** This document should be the PRIMARY reference during implementation. Every checkbox must be completed before submission.

