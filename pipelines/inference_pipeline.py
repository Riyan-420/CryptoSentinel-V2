"""Inference Pipeline - Generate predictions"""
import logging
from datetime import datetime
from prefect import flow, task

from app.data_fetcher import fetch_current_price, fetch_price_history
from app.feature_engineering import engineer_features
from app.predictor import generate_prediction, validate_predictions
from app.alerts import check_alerts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task(name="get_current_data")
def get_current_data():
    """Fetch current price and recent history"""
    logger.info("Fetching current market data")
    current = fetch_current_price()
    history = fetch_price_history(hours=6)
    return current, history

@task(name="prepare_features")
def prepare_features(history):
    """Prepare features for prediction"""
    logger.info("Preparing features")
    features = engineer_features(history)
    return features

@task(name="run_prediction")
def run_prediction(features, current_price):
    """Generate prediction"""
    logger.info("Generating prediction")
    prediction = generate_prediction(features, current_price)
    return prediction

@task(name="validate_past_predictions")
def validate_past_predictions(current_price):
    """Validate past predictions"""
    logger.info("Validating predictions")
    validate_predictions(current_price)

@task(name="check_for_alerts")
def check_for_alerts(current, prediction, features):
    """Check alert conditions"""
    logger.info("Checking alerts")
    volatility = None
    if 'volatility' in features.columns:
        volatility = features['volatility'].iloc[-1]
    previous_price = current["current_price"] - current.get("change_24h", 0)
    alerts = check_alerts(
        current_price=current["current_price"],
        previous_price=previous_price,
        prediction=prediction,
        volatility=volatility
    )
    return alerts

@flow(name="inference_pipeline")
def inference_pipeline():
    logger.info("Starting Inference Pipeline")
    start_time = datetime.now()
    current, history = get_current_data()
    current_price = current["current_price"]
    features = prepare_features(history)
    prediction = run_prediction(features, current_price)
    validate_past_predictions(current_price)
    alerts = check_for_alerts(current, prediction, features)
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"Inference complete ({duration:.2f}s)")
    return {
        "current_price": current_price,
        "prediction": prediction,
        "alerts": alerts,
        "duration_seconds": duration,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    result = inference_pipeline()
    print(result)

