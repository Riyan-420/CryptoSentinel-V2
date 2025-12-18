# 🚀 CryptoSentinel V2 - Complete Deployment Guide

## 📋 Prerequisites

Before deploying, ensure you have accounts and credentials for:

1. ✅ **Hopsworks** - Feature Store & Model Registry
2. ✅ **Prefect Cloud** - Reliable pipeline scheduling
3. ✅ **Hugging Face** - Streamlit app hosting
4. ✅ **GitHub** - Code repository

---

## 🔐 Step 1: Configure GitHub Secrets

Add these secrets to your GitHub repository:
`https://github.com/Riyan-420/CryptoSentinel-V2/settings/secrets/actions`

### Required Secrets:

| Secret Name | Value | Purpose |
|-------------|-------|---------|
| `HOPSWORKS_API_KEY` | Your Hopsworks API key | Access Feature Store & Model Registry |
| `HOPSWORKS_PROJECT_NAME` | `CryptoSentinel` | Hopsworks project name |
| `HF_TOKEN` | Your Hugging Face token | Deploy to HF Spaces |
| `HF_REPO_ID` | `your-username/CryptoSentinel-V2` | Target HF Space |
| `PREFECT_API_URL` | Your Prefect workspace URL | Connect to Prefect Cloud |
| `PREFECT_API_KEY` | Your Prefect API key | Authenticate with Prefect |

---

## 🌐 Step 2: Deploy to Hugging Face Spaces

### Method 1: Automatic GitHub Sync (Recommended) ✨

1. **Create Hugging Face Space:**
   - Go to: https://huggingface.co/new-space
   - Name: `CryptoSentinel-V2`
   - SDK: **Docker**
   - Hardware: **CPU basic (free)**

2. **Add HF_REPO_ID Secret to GitHub:**
   ```
   HF_REPO_ID=your-username/CryptoSentinel-V2
   ```

3. **Push to GitHub:**
   ```bash
   git push origin master
   ```

4. **Auto-Deploy:**
   - GitHub Actions will automatically sync to HF Space
   - Check workflow: `.github/workflows/deploy_to_hf.yml`
   - Monitor: https://github.com/Riyan-420/CryptoSentinel-V2/actions

5. **Configure HF Space Secrets:**
   - Go to: `https://huggingface.co/spaces/YOUR_USERNAME/CryptoSentinel-V2/settings`
   - Add secrets:
     ```
     HOPSWORKS_API_KEY=your-key
     HOPSWORKS_PROJECT_NAME=CryptoSentinel
     ```

### Method 2: Manual Deployment

```bash
# Install HF CLI
pip install huggingface_hub

# Login
huggingface-cli login

# Upload
python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_folder(
    folder_path='.',
    repo_id='YOUR_USERNAME/CryptoSentinel-V2',
    repo_type='space'
)
"
```

---

## ⚙️ Step 3: Set Up Prefect Cloud Scheduling

### Why Prefect Instead of GitHub Actions?

- ✅ **Reliable** - No delays (unlike GitHub cron)
- ✅ **Precise** - True 5-minute intervals
- ✅ **Monitoring** - Real-time pipeline status
- ✅ **Free tier** - 20,000 runs/month

### Configure Prefect:

1. **Login to Prefect:**
   ```bash
   prefect cloud login
   ```
   Use API key: `pnu_UokYz4NGYXtSDlJAsyM7E77x0MU54R0SrRLe`

2. **Deploy Feature Pipeline:**
   ```bash
   python -c "
   from prefect.deployments import Deployment
   from prefect.server.schemas.schedules import IntervalSchedule
   from datetime import timedelta
   from pipelines.feature_pipeline import feature_pipeline
   
   deployment = Deployment.build_from_flow(
       flow=feature_pipeline,
       name='feature-pipeline-prod',
       schedule=IntervalSchedule(interval=timedelta(minutes=5)),
       work_queue_name='default'
   )
   deployment.apply()
   "
   ```

3. **Deploy Training Pipeline:**
   ```bash
   python -c "
   from prefect.deployments import Deployment
   from prefect.server.schemas.schedules import IntervalSchedule
   from datetime import timedelta
   from pipelines.training_pipeline import training_pipeline
   
   deployment = Deployment.build_from_flow(
       flow=training_pipeline,
       name='training-pipeline-prod',
       schedule=IntervalSchedule(interval=timedelta(minutes=30)),
       work_queue_name='default'
   )
   deployment.apply()
   "
   ```

4. **Start Prefect Agent:**
   ```bash
   prefect agent start -q default
   ```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────┐
│   HUGGING FACE SPACES (Public Frontend)    │
│   • Streamlit Dashboard                     │
│   • Live Predictions                        │
│   • Model Insights & Visualizations         │
│   URL: https://hf.co/spaces/user/crypto     │
└────────────────┬────────────────────────────┘
                 │
                 ↓ (loads from)
┌─────────────────────────────────────────────┐
│   HOPSWORKS (Data & Model Layer)            │
│   • Feature Store (fresh data every 5min)   │
│   • Model Registry (best models)            │
│   URL: https://c.app.hopsworks.ai           │
└────────────────┬────────────────────────────┘
                 │
                 ↑ (updated by)
┌─────────────────────────────────────────────┐
│   PREFECT CLOUD (Pipeline Orchestration)    │
│   • Feature Pipeline (every 5 min)          │
│   • Training Pipeline (every 30 min)        │
│   URL: https://app.prefect.cloud            │
└─────────────────────────────────────────────┘
```

---

## 🔄 CI/CD Workflows

### 1. Feature Pipeline (Every 5 minutes via Prefect)
```
Fetch BTC Price → Engineer Features → Upload to Hopsworks
```

### 2. Training Pipeline (Every 30 minutes via Prefect)
```
Load Features → Train Models → Detect Drift → Register Best Model
```

### 3. GitHub Actions CI (On every push)
```
Lint Code → Test Imports → Verify Structure
```

### 4. GitHub Actions Deploy (On push to master)
```
Build Docker Image → Push to Hugging Face Space
```

---

## 🧪 Local Testing

### Run All Pipelines Locally:
```bash
python run_all.py
```

### Run Streamlit Dashboard:
```bash
streamlit run dashboard.py
```

### Docker Local Test:
```bash
docker build -t cryptosentinel .
docker run -p 7860:7860 --env-file .env cryptosentinel
```

---

## 📊 Monitoring & URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **HF Space** | https://huggingface.co/spaces/YOUR_USERNAME/CryptoSentinel-V2 | Live Dashboard |
| **Hopsworks** | https://c.app.hopsworks.ai/p/1327255 | Feature Store & Models |
| **Prefect** | https://app.prefect.cloud | Pipeline Monitoring |
| **GitHub Actions** | https://github.com/Riyan-420/CryptoSentinel-V2/actions | CI/CD Status |

---

## 🐛 Troubleshooting

### Issue: Streamlit app not loading on HF
**Solution:** Check HF Space logs, ensure secrets are set

### Issue: Models not found
**Solution:** Run training pipeline first: `python -m pipelines.training_pipeline`

### Issue: Hopsworks connection failed
**Solution:** Verify API key is correct and project name matches exactly

### Issue: Prefect pipelines not running
**Solution:** Ensure agent is running: `prefect agent start -q default`

---

## 🎉 Success Checklist

- [ ] GitHub secrets configured
- [ ] Hugging Face Space created
- [ ] HF Space secrets added
- [ ] Prefect pipelines deployed
- [ ] Prefect agent running
- [ ] First training run completed
- [ ] Streamlit dashboard accessible
- [ ] Real-time predictions working

---

## 📝 Notes

- **Free Tier Limits:**
  - HF Spaces: Sleep after 48h inactivity
  - Hopsworks: 10GB storage, 5GB/day processing
  - Prefect: 20,000 runs/month
  - GitHub Actions: Unlimited (public repo)

- **Cost Optimization:**
  - Models stored in Hopsworks (not Git)
  - Docker multi-stage build (smaller image)
  - Selective file sync to HF

- **For Production:**
  - Upgrade HF Space hardware (paid)
  - Add monitoring/alerting
  - Implement proper logging
  - Set up backup strategies

---

**Need Help?** Check logs in each service's dashboard or create an issue on GitHub!


