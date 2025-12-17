"""Training Pipeline - Train models and register in Hopsworks"""
import logging
from datetime import datetime
from prefect import flow, task

from app.config import settings
from app.feature_engineering import get_feature_names
from app.model_trainer import (
    train_regression_models, train_classifier, train_kmeans,
    select_best_model, save_models, promote_to_active
)
from storage.feature_store import fetch_features
from storage.model_registry import register_model_bundle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task(name="load_features")
def load_features():
    """Load features from Feature Store"""
    logger.info("Loading features from Feature Store")
    df = fetch_features()
    
    if df is None or len(df) < 50:
        raise ValueError("Insufficient feature data for training")
    
    logger.info(f"Loaded {len(df)} feature rows")
    return df


@task(name="check_drift")
def check_drift_task(features_df):
    """Check for data drift"""
    from app.drift_detection import detect_drift
    
    feature_cols = get_feature_names()
    available_cols = [c for c in feature_cols if c in features_df.columns]
    
    logger.info("Checking for data drift...")
    drift_report = detect_drift(features_df, available_cols)
    
    if drift_report.get('drift_detected'):
        logger.warning(f"⚠️  Drift detected! Score: {drift_report.get('drift_score', 0):.4f}")
    else:
        logger.info(f"✓ No drift detected. Score: {drift_report.get('drift_score', 0):.4f}")
    
    return drift_report


@task(name="prepare_training_data")
def prepare_training_data(features_df):
    """Prepare X and y for training"""
    feature_cols = get_feature_names()
    available_cols = [c for c in feature_cols if c in features_df.columns]
    
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
    
    return X, y_price, y_direction, available_cols


@task(name="train_all_models")
def train_all_models(X, y_price, y_direction):
    """Train all models"""
    logger.info("Training regression models")
    regression_results, scaler = train_regression_models(X, y_price)
    
    logger.info("Training classifier")
    classifier, classifier_metrics = train_classifier(X, y_direction)
    
    logger.info("Training K-Means clustering")
    kmeans, pca = train_kmeans(X, settings.N_CLUSTERS)
    
    # Combine all models
    models = {name: model for name, (model, _) in regression_results.items()}
    models["classifier"] = classifier
    models["kmeans"] = kmeans
    models["pca"] = pca
    
    # Collect metrics
    metrics = {
        name: m for name, (_, m) in regression_results.items()
    }
    metrics["classifier"] = classifier_metrics
    
    # Find best regression model
    best_name = select_best_model(regression_results)
    
    return models, scaler, metrics, best_name


@task(name="set_drift_baseline")
def set_drift_baseline_task(features_df, feature_cols):
    """Set reference data for future drift detection"""
    from app.drift_detection import set_reference_data
    
    logger.info("Setting reference baseline for drift detection...")
    set_reference_data(features_df[feature_cols])
    logger.info("✓ Baseline set for next drift check")


@task(name="save_and_register_models")
def save_and_register_models(models, scaler, metrics, best_name):
    """Save models locally and register in Hopsworks"""
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    metadata = {
        "version": version,
        "best_model": best_name,
        "metrics": metrics.get(best_name, {}),
        "created_at": datetime.now().isoformat(),
        "feature_names": get_feature_names()
    }
    
    # Save locally
    logger.info("Saving models locally")
    save_dir = save_models(models, scaler, best_name, version)
    
    # Promote to active
    promote_to_active(save_dir)
    
    # Register in Hopsworks
    logger.info("Registering in Hopsworks Model Registry")
    hw_model = register_model_bundle(models, scaler, metadata)
    
    return {
        "local_path": str(save_dir),
        "hopsworks_registered": hw_model is not None,
        "version": version,
        "best_model": best_name
    }


@flow(name="training_pipeline")
def training_pipeline():
    """
    Main training pipeline flow.
    
    1. Load features from Hopsworks Feature Store
    2. Check for data drift
    3. Prepare training data
    4. Train multiple models (XGBoost, RF, GB, Ridge, Classifier, K-Means)
    5. Select best model
    6. Save locally and register in Hopsworks Model Registry
    7. Set reference baseline for next drift check
    """
    logger.info("=== Starting Training Pipeline ===")
    start_time = datetime.now()
    
    # Load features
    features_df = load_features()
    
    # Check drift
    drift_report = check_drift_task(features_df)
    
    # Prepare data
    X, y_price, y_direction, feature_cols = prepare_training_data(features_df)
    
    # Train models
    models, scaler, metrics, best_name = train_all_models(X, y_price, y_direction)
    
    # Save and register
    result = save_and_register_models(models, scaler, metrics, best_name)
    
    # Set reference for next drift check
    set_drift_baseline_task(features_df, feature_cols)
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"=== Training Pipeline Complete ({duration:.2f}s) ===")
    
    return {
        **result,
        "duration_seconds": duration,
        "samples_trained": len(X),
        "metrics": metrics,
        "drift_report": drift_report,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    result = training_pipeline()
    print(result)

