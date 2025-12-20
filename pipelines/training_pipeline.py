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
    logger.info("Loading features")
    df = fetch_features()
    if df is None or len(df) < 50:
        raise ValueError("Insufficient data")
    logger.info(f"Loaded {len(df)} rows")
    return df

@task(name="check_drift")
def check_drift_task(features_df):
    from app.drift_detection import detect_drift
    feature_cols = get_feature_names()
    available_cols = [c for c in feature_cols if c in features_df.columns]
    logger.info("Checking drift")
    drift_report = detect_drift(features_df, available_cols)
    if drift_report.get('drift_detected'):
        logger.warning(f"Drift: {drift_report.get('drift_score', 0):.4f}")
    else:
        logger.info(f"No drift: {drift_report.get('drift_score', 0):.4f}")
    return drift_report

@task(name="prepare_training_data")
def prepare_training_data(features_df):
    feature_cols = get_feature_names()
    available_cols = [c for c in feature_cols if c in features_df.columns]
    X = features_df[available_cols].copy()
    y_price = features_df.get('future_price', features_df['price'].shift(-1))
    y_direction = features_df.get('target_direction', (y_price > features_df['price']).astype(int))
    valid_idx = ~(X.isnull().any(axis=1) | y_price.isnull())
    X, y_price, y_direction = X[valid_idx], y_price[valid_idx], y_direction[valid_idx]
    
    # Log training data distribution
    up_count = (y_direction == 1).sum()
    down_count = (y_direction == 0).sum()
    up_pct = (up_count / len(y_direction)) * 100 if len(y_direction) > 0 else 0
    logger.info(f"Prepared {len(X)} samples, {len(available_cols)} features")
    logger.info(f"Direction distribution: UP={up_count} ({up_pct:.1f}%), DOWN={down_count} ({100-up_pct:.1f}%)")
    
    return X, y_price, y_direction, available_cols

@task(name="train_all_models")
def train_all_models(X, y_price, y_direction):
    logger.info("Training models")
    regression_results, scaler = train_regression_models(X, y_price)
    classifier, classifier_metrics = train_classifier(X, y_direction)
    kmeans, pca = train_kmeans(X, settings.N_CLUSTERS)
    models = {name: model for name, (model, _) in regression_results.items()}
    models.update({"classifier": classifier, "kmeans": kmeans, "pca": pca})
    metrics = {name: m for name, (_, m) in regression_results.items()}
    metrics["classifier"] = classifier_metrics
    best_name = select_best_model(regression_results)
    return models, scaler, metrics, best_name

@task(name="set_drift_baseline")
def set_drift_baseline_task(features_df, feature_cols):
    from app.drift_detection import set_reference_data
    logger.info("Setting drift baseline")
    set_reference_data(features_df[feature_cols])

@task(name="clear_old_predictions")
def clear_old_predictions_task():
    from storage.prediction_store import clear_prediction_history
    logger.info("Clearing old prediction history")
    success = clear_prediction_history()
    if success:
        logger.info("Prediction history cleared successfully")
    else:
        logger.warning("Failed to clear prediction history")

@task(name="save_and_register_models")
def save_and_register_models(models, scaler, metrics, best_name):
    version = datetime.now().strftime("%Y%m%d_%H%M%S")
    metadata = {
        "version": version,
        "best_model": best_name,
        "metrics": metrics.get(best_name, {}),
        "created_at": datetime.now().isoformat(),
        "feature_names": get_feature_names()
    }
    logger.info("Saving models")
    save_dir = save_models(models, scaler, best_name, version)
    promote_to_active(save_dir)
    logger.info("Registering in Hopsworks")
    hw_model = register_model_bundle(models, scaler, metadata)
    return {
        "local_path": str(save_dir),
        "hopsworks_registered": hw_model is not None,
        "version": version,
        "best_model": best_name
    }

@flow(name="training_pipeline")
def training_pipeline():
    logger.info("Starting Training Pipeline")
    start_time = datetime.now()
    features_df = load_features()
    drift_report = check_drift_task(features_df)
    X, y_price, y_direction, feature_cols = prepare_training_data(features_df)
    models, scaler, metrics, best_name = train_all_models(X, y_price, y_direction)
    result = save_and_register_models(models, scaler, metrics, best_name)
    clear_old_predictions_task()
    set_drift_baseline_task(features_df, feature_cols)
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"Training complete ({duration:.2f}s)")
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
