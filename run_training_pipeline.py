"""Direct execution of training pipeline (for GitHub Actions)"""
import logging
import sys
from datetime import datetime

from app.config import settings
from app.feature_engineering import get_feature_names
from app.model_trainer import (
    train_regression_models, train_classifier, train_kmeans,
    select_best_model, save_models, promote_to_active
)
from app.drift_detection import detect_drift, set_reference_data
from storage.feature_store import fetch_features
from storage.model_registry import register_model_bundle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run training pipeline directly (without Prefect)"""
    logger.info("=== Starting Training Pipeline (Direct Execution) ===")
    start_time = datetime.now()
    
    try:
        # Load features
        logger.info("Loading features from Feature Store...")
        features_df = fetch_features()
        
        if features_df is None or len(features_df) < 50:
            logger.error("Insufficient feature data for training")
            return 1
        
        logger.info(f"Loaded {len(features_df)} feature rows")
        
        # Check drift
        logger.info("Checking for data drift...")
        feature_cols = get_feature_names()
        available_cols = [c for c in feature_cols if c in features_df.columns]
        drift_report = detect_drift(features_df, available_cols)
        
        if drift_report.get('drift_detected'):
            logger.warning(f"⚠️  Drift detected! Score: {drift_report.get('drift_score', 0):.4f}")
        else:
            logger.info(f"✓ No drift detected. Score: {drift_report.get('drift_score', 0):.4f}")
        
        # Prepare training data
        logger.info("Preparing training data...")
        X = features_df[available_cols].copy()
        
        if 'future_price' in features_df.columns:
            y_price = features_df['future_price']
        else:
            y_price = features_df['price'].shift(-1)
        
        if 'target_direction' in features_df.columns:
            y_direction = features_df['target_direction']
        else:
            y_direction = (y_price > features_df['price']).astype(int)
        
        # Drop NaN rows
        valid_idx = ~(X.isnull().any(axis=1) | y_price.isnull())
        X = X[valid_idx]
        y_price = y_price[valid_idx]
        y_direction = y_direction[valid_idx]
        
        logger.info(f"Prepared {len(X)} samples with {len(available_cols)} features")
        
        # Train models
        logger.info("Training regression models...")
        regression_results, scaler = train_regression_models(X, y_price)
        
        logger.info("Training classifier...")
        classifier, classifier_metrics = train_classifier(X, y_direction)
        
        logger.info("Training K-Means clustering...")
        kmeans, pca = train_kmeans(X, settings.N_CLUSTERS)
        
        # Combine all models
        models = {name: model for name, (model, _) in regression_results.items()}
        models["classifier"] = classifier
        models["kmeans"] = kmeans
        models["pca"] = pca
        
        # Collect metrics
        metrics = {name: m for name, (_, m) in regression_results.items()}
        metrics["classifier"] = classifier_metrics
        
        # Find best regression model
        best_name = select_best_model(regression_results)
        logger.info(f"Best model: {best_name}")
        
        # Save and register
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata = {
            "version": version,
            "best_model": best_name,
            "metrics": metrics.get(best_name, {}),
            "created_at": datetime.now().isoformat(),
            "feature_names": get_feature_names()
        }
        
        logger.info("Saving models locally...")
        save_dir = save_models(models, scaler, best_name, version)
        promote_to_active(save_dir)
        
        logger.info("Registering in Hopsworks Model Registry...")
        hw_model = register_model_bundle(models, scaler, metadata)
        
        # Set reference for next drift check
        logger.info("Setting reference baseline for drift detection...")
        set_reference_data(features_df[available_cols])
        
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"✅ Training Pipeline Complete ({duration:.2f}s)")
        logger.info(f"Models saved to: {save_dir}")
        logger.info(f"Hopsworks registration: {'Success' if hw_model else 'Failed'}")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Training Pipeline Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())

