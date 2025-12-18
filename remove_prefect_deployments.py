"""Remove Prefect Cloud deployments to avoid duplicate runs with GitHub Actions"""
from prefect import get_client

def remove_deployments():
    """Remove feature and training pipeline deployments from Prefect Cloud"""
    with get_client() as client:
        try:
            deployments = client.read_deployments()
            
            for deployment in deployments:
                if deployment.name in ["feature-pipeline-prod", "training-pipeline-prod"]:
                    print(f"Removing deployment: {deployment.name}")
                    client.delete_deployment(deployment.id)
                    print(f"✓ Removed: {deployment.name}")
            
            print("\n" + "="*70)
            print("Prefect deployments removed. Using GitHub Actions only.")
            print("="*70)
        except Exception as e:
            print(f"Error removing deployments: {e}")

if __name__ == "__main__":
    remove_deployments()

