# Hugging Face Spaces Deployment Guide

## How CryptoSentinel Works on Hugging Face Spaces

### ✅ What WORKS on HF Spaces (Cloud Deployment)

1. **Background Automation**
   - ✅ Background scheduler runs automatically on app startup
   - ✅ Feature pipeline runs every 5 minutes (fetches new data)
   - ✅ Training pipeline runs every 30 minutes (retrains models)
   - ✅ Inference pipeline runs every 5 minutes (generates predictions)
   - ✅ Predictions update automatically without page reload

2. **Data Persistence**
   - ✅ Features stored in Hopsworks Feature Store (persistent)
   - ✅ Models stored in Hopsworks Model Registry (persistent)
   - ✅ **Predictions stored in Hopsworks** (NEW - persistent across restarts)
   - ✅ All data survives app restarts/rebuilds

3. **Model Management**
   - ✅ Models automatically reload from Hopsworks after training
   - ✅ Best model selection happens automatically
   - ✅ Model versioning tracked in Hopsworks

4. **Real-time Updates**
   - ✅ Live price data from CoinGecko API
   - ✅ Automatic prediction generation
   - ✅ Automatic prediction validation
   - ✅ Real-time drift detection

### ⚠️ Limitations on HF Spaces

1. **Ephemeral File System**
   - Local files (`predictions_history.json`) don't persist across restarts
   - **SOLUTION**: Predictions are backed up to Hopsworks Feature Store
   - On app restart, predictions are loaded from Hopsworks

2. **GitHub Actions Don't Directly Affect Running App**
   - GitHub Actions run feature/training pipelines independently
   - Data is stored in Hopsworks
   - **Running app pulls fresh data from Hopsworks** (not from GitHub Actions directly)
   - Both systems work together through Hopsworks as the central hub

3. **Single Instance**
   - Only one instance of the app runs (no horizontal scaling)
   - Background scheduler runs in the same process
   - This is fine for this use case

## Architecture Flow on HF Spaces

```
┌─────────────────────────────────────────────────────────────┐
│                   GITHUB ACTIONS (Every 5/30 min)           │
│  ┌──────────────┐              ┌──────────────┐            │
│  │   Feature    │              │   Training   │            │
│  │   Pipeline   │              │   Pipeline   │            │
│  └──────┬───────┘              └──────┬───────┘            │
└─────────┼──────────────────────────────┼──────────────────┘
          │                              │
          ▼                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  HOPSWORKS (Central Hub)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Feature    │  │    Model     │  │  Prediction  │     │
│  │    Store     │  │   Registry   │  │    History   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
          ▲                              ▲
          │                              │
          │     ┌────────────────────────┘
          │     │
┌─────────┴─────┴─────────────────────────────────────────────┐
│            HUGGING FACE SPACES (Always Running)              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  STREAMLIT APP + BACKGROUND SCHEDULER                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │   Feature   │  │   Training  │  │  Inference  │  │  │
│  │  │  (5 min)    │  │  (30 min)   │  │  (5 min)    │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │  - Fetches features from Hopsworks                    │  │
│  │  - Loads models from Hopsworks                        │  │
│  │  - Generates predictions automatically                │  │
│  │  - Stores predictions in Hopsworks                    │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  User sees: Real-time dashboard with auto-updating          │
│            predictions every 5 minutes                       │
└─────────────────────────────────────────────────────────────┘
```

## Key Changes for Cloud Deployment

### 1. Prediction Persistence (`storage/prediction_store.py`)
- Predictions are now stored in Hopsworks Feature Store
- On app startup, predictions are loaded from Hopsworks
- Fallback to local file if Hopsworks unavailable

### 2. Background Scheduler (`app/scheduler.py`)
- Runs 3 pipelines automatically:
  - Feature pipeline (every 5 min)
  - Training pipeline (every 30 min)  
  - **Inference pipeline (every 5 min)** ← NEW
- Automatically reloads models after training
- Starts immediately when app launches

### 3. Model Auto-Reload
- After training completes, models are automatically reloaded from Hopsworks
- Ensures predictions always use the latest model
- No manual intervention required

## Testing on HF Spaces

1. **Deploy to HF Spaces** (automatic via GitHub Actions)
2. **Wait 1-2 minutes** for background scheduler to start
3. **Check Dashboard**: You should see:
   - Current prediction generated automatically
   - Predictions updating every 5 minutes without page reload
4. **Check Hopsworks**: You should see:
   - Feature Store updates every 5 minutes
   - Model Registry updates every 30 minutes
   - Prediction history feature group (new data every 5 min)

## Monitoring

### Via Streamlit Dashboard
- Go to "Pipeline Control" page
- See last run times for all pipelines
- Check scheduler status

### Via Hopsworks
- **Feature Store**: `crypto_features` updates every 5 min
- **Model Registry**: `crypto_model_bundle` new versions every 30 min
- **Prediction Store**: `prediction_history` updates every 5 min

### Via GitHub Actions
- Check workflow runs for feature/training pipelines
- These run independently but store data in same Hopsworks project

## Dual Automation System

**Why both GitHub Actions AND Background Scheduler?**

1. **GitHub Actions** (Primary)
   - Reliable external scheduler
   - Runs even if HF Spaces app crashes
   - Updates Hopsworks regularly

2. **Background Scheduler in App** (Failsafe + Inference)
   - Generates predictions locally in the running app
   - Ensures predictions update automatically in UI
   - Can run pipelines even if GitHub Actions delayed
   - **Runs inference pipeline** (GitHub Actions doesn't run this)

3. **Together**
   - Maximum reliability
   - Data always fresh in Hopsworks
   - Predictions always up-to-date in app
   - User sees live updates without refresh

## FAQ

**Q: Do predictions persist across app restarts?**  
A: Yes! Predictions are stored in Hopsworks Feature Store.

**Q: Will predictions update automatically without reload?**  
A: Yes! Background scheduler runs inference every 5 minutes.

**Q: Does GitHub Actions data sync with the app?**  
A: Yes! Both read/write to Hopsworks, which is the central hub.

**Q: What happens if Hopsworks is down?**  
A: App falls back to local storage (ephemeral but functional).

**Q: How long until first prediction appears?**  
A: ~1-2 minutes after app starts (background scheduler init).

**Q: Can I manually trigger pipelines?**  
A: Yes! Use the "Pipeline Control" page in the dashboard.

## Summary

✅ **Everything works on HF Spaces**  
✅ **Predictions update automatically every 5 minutes**  
✅ **No page reload needed**  
✅ **Data persists across restarts via Hopsworks**  
✅ **GitHub Actions + App work together seamlessly**

