"""Deploy CryptoSentinel pipelines to Prefect Cloud with reliable scheduling"""
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import IntervalSchedule
from datetime import timedelta
from pipelines.feature_pipeline import feature_pipeline
from pipelines.training_pipeline import training_pipeline

print("🚀 Deploying pipelines to Prefect Cloud...")

# Deploy Feature Pipeline (every 5 minutes)
print("\n1️⃣ Deploying Feature Pipeline (every 5 min)...")
feature_deployment = Deployment.build_from_flow(
    flow=feature_pipeline,
    name="feature-pipeline-prod",
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    work_queue_name="default",
    tags=["production", "crypto", "features"]
)
feature_deployment.apply()
print("✅ Feature Pipeline deployed!")

# Deploy Training Pipeline (every 30 minutes)
print("\n2️⃣ Deploying Training Pipeline (every 30 min)...")
training_deployment = Deployment.build_from_flow(
    flow=training_pipeline,
    name="training-pipeline-prod",
    schedule=IntervalSchedule(interval=timedelta(minutes=30)),
    work_queue_name="default",
    tags=["production", "crypto", "training"]
)
training_deployment.apply()
print("✅ Training Pipeline deployed!")

print("\n" + "="*70)
print("🎉 ALL PIPELINES DEPLOYED TO PREFECT CLOUD!")
print("="*70)
print("\n📋 Next Steps:")
print("1. Start Prefect agent: prefect agent start -q default")
print("2. View dashboard: https://app.prefect.cloud")
print("\n⏰ Schedules:")
print("   • Feature Pipeline: Every 5 minutes")
print("   • Training Pipeline: Every 30 minutes")
print("\n✨ These will run RELIABLY unlike GitHub Actions!")

