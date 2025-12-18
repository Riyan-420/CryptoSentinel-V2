"""Deploy CryptoSentinel pipelines to Prefect Cloud with reliable scheduling"""
from datetime import timedelta
from prefect.client.schemas.schedules import IntervalSchedule
from pipelines.feature_pipeline import feature_pipeline
from pipelines.training_pipeline import training_pipeline

print("Deploying pipelines to Prefect Cloud...")
print("Creating deployments...\n")

# Create deployments with schedules
feature_deployment = feature_pipeline.to_deployment(
    name="feature-pipeline-prod",
    tags=["production", "crypto", "features"],
    schedule=IntervalSchedule(interval=timedelta(minutes=5))
)

training_deployment = training_pipeline.to_deployment(
    name="training-pipeline-prod",
    tags=["production", "crypto", "training"],
    schedule=IntervalSchedule(interval=timedelta(minutes=30))
)

# Apply deployments to Prefect Cloud
print("1️⃣ Deploying Feature Pipeline (every 5 min)...")
try:
    feature_deployment.apply()
    print("Feature Pipeline deployed!")
except Exception as e:
    print(f"Error deploying Feature Pipeline: {e}")

print("\n2️⃣ Deploying Training Pipeline (every 30 min)...")
try:
    training_deployment.apply()
    print("Training Pipeline deployed!")
except Exception as e:
    print(f"Error deploying Training Pipeline: {e}")

print("\n" + "="*70)
print("DEPLOYMENT COMPLETE!")
print("="*70)
print("\nNext Steps:")
print("1. View deployments in Prefect Cloud: https://app.prefect.cloud")
print("2. Pipelines will run automatically on schedule")
print("\nSchedules:")
print("   - Feature Pipeline: Every 5 minutes")
print("   - Training Pipeline: Every 30 minutes")


