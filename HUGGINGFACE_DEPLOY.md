# 🚀 Deploy CryptoSentinel to Hugging Face Spaces

## Quick Deployment Steps

### 1. Create a New Space

1. Go to: https://huggingface.co/new-space
2. Fill in:
   - **Space name**: `CryptoSentinel-V2`
   - **License**: MIT
   - **Select the SDK**: Streamlit
   - **Space hardware**: CPU basic (free tier)
   - **Visibility**: Public

### 2. Clone Your Space Repository

```bash
git clone https://huggingface.co/spaces/YOUR_USERNAME/CryptoSentinel-V2
cd CryptoSentinel-V2
```

### 3. Copy Project Files

Copy these files from your CryptoSentinel project:

```bash
# Copy all necessary files
cp -r app/ pages/ pipelines/ storage/ .streamlit/ dashboard.py requirements.txt README_HF.md packages.txt CryptoSentinel-V2/

# Rename README for Hugging Face
cd CryptoSentinel-V2
mv README_HF.md README.md
```

### 4. Configure Secrets

1. Go to your Space settings: `https://huggingface.co/spaces/YOUR_USERNAME/CryptoSentinel-V2/settings`
2. Scroll to **"Repository secrets"**
3. Add these secrets:

   ```
   HOPSWORKS_API_KEY = your-actual-api-key-here
   HOPSWORKS_PROJECT_NAME = CryptoSentinel
   TRAINING_INTERVAL_MINUTES = 30
   PREDICTION_REFRESH_MINUTES = 5
   DIRECTION_TOLERANCE_PCT = 0.1
   ```

### 5. Push to Hugging Face

```bash
git add .
git commit -m "Initial deployment of CryptoSentinel V2"
git push
```

### 6. Wait for Build

- Hugging Face will automatically build and deploy your app
- Build time: ~5-10 minutes
- You can watch the build logs in the "Logs" tab

---

## ⚠️ Important Notes

### Free Tier Limitations

- **CPU**: Basic (free) - sufficient for this app
- **Memory**: 16GB RAM
- **Sleep**: Spaces sleep after 48 hours of inactivity
- **No persistent storage**: Models will reload from Hopsworks on restart

### What Works on Hugging Face

✅ Streamlit dashboard
✅ Load models from Hopsworks
✅ Make predictions
✅ Display drift reports
✅ All visualizations

### What Doesn't Work on Hugging Face

❌ Training pipelines (not enough compute)
❌ Scheduled jobs (use GitHub Actions for this)
❌ FastAPI backend (Streamlit only)

**Solution**: Keep GitHub Actions for training/features (cloud), use HF Space for UI only!

---

## Alternative: Simple Push Method

If you want to deploy directly from your current GitHub repo:

1. Create Space on Hugging Face
2. Go to Space settings
3. Under "Files and versions", click "Link to GitHub"
4. Connect `Riyan-420/CryptoSentinel-V2`
5. Select `master` branch
6. Add the secrets
7. Done! Auto-deploys on every push

---

## Troubleshooting

### Build Fails

- Check build logs
- Ensure all dependencies in `requirements.txt` are compatible
- Check `packages.txt` for system dependencies

### App Crashes

- Check "Logs" tab in your Space
- Ensure Hopsworks secrets are set correctly
- Verify models exist in Hopsworks

### Slow Performance

- Upgrade to better hardware (paid)
- Or optimize model loading (cache models)

---

## URL

After deployment, your app will be at:
```
https://huggingface.co/spaces/YOUR_USERNAME/CryptoSentinel-V2
```

Share this link for demos! 🎉

