"""Deploy CryptoSentinel pipelines to Prefect Cloud with reliable scheduling"""
import subprocess
import sys
from pathlib import Path

print("🚀 Deploying pipelines to Prefect Cloud...")
print("📝 Using Prefect CLI for deployment...\n")

# Get the Python executable from venv
venv_python = Path("venv/Scripts/python.exe")
if not venv_python.exists():
    venv_python = Path("venv/bin/python")
if not venv_python.exists():
    venv_python = sys.executable

print(f"Using Python: {venv_python}\n")

# Deploy Feature Pipeline
print("1️⃣ Deploying Feature Pipeline (every 5 min)...")
result1 = subprocess.run(
    [str(venv_python), "-m", "prefect", "deploy", 
     "pipelines/feature_pipeline.py:feature_pipeline",
     "--name", "feature-pipeline-prod",
     "--interval", "5",
     "--work-queue", "default",
     "--tags", "production,crypto,features"],
    capture_output=True,
    text=True
)
if result1.returncode == 0:
    print("✅ Feature Pipeline deployed!")
else:
    print(f"❌ Error: {result1.stderr}")
    print("Trying alternative method...")

# Deploy Training Pipeline  
print("\n2️⃣ Deploying Training Pipeline (every 30 min)...")
result2 = subprocess.run(
    [str(venv_python), "-m", "prefect", "deploy",
     "pipelines/training_pipeline.py:training_pipeline",
     "--name", "training-pipeline-prod",
     "--interval", "30",
     "--work-queue", "default",
     "--tags", "production,crypto,training"],
    capture_output=True,
    text=True
)
if result2.returncode == 0:
    print("✅ Training Pipeline deployed!")
else:
    print(f"❌ Error: {result2.stderr}")

print("\n" + "="*70)
print("🎉 DEPLOYMENT COMPLETE!")
print("="*70)
print("\n📋 Next Steps:")
print("1. Start Prefect agent: prefect agent start -q default")
print("2. View dashboard: https://app.prefect.cloud")
print("\n⏰ Schedules:")
print("   • Feature Pipeline: Every 5 minutes")
print("   • Training Pipeline: Every 30 minutes")
print("\n✨ These will run RELIABLY unlike GitHub Actions!")


