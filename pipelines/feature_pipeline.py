"""Feature Pipeline - Fetch data and engineer features"""
import logging
from datetime import datetime
from prefect import flow, task

from app.data_fetcher import fetch_price_history
from app.feature_engineering import engineer_features
from storage.feature_store import store_features

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@task(name="fetch_price_data", retries=3, retry_delay_seconds=30)
def fetch_price_data(hours: int = 24):
    """Fetch price history from CoinGecko"""
    logger.info(f"Fetching {hours} hours of price data")
    data = fetch_price_history(hours)
    logger.info(f"Fetched {len(data)} price points")
    return data


@task(name="engineer_features_task")
def engineer_features_task(price_data):
    """Engineer features from price data"""
    logger.info("Engineering features")
    df = engineer_features(price_data)
    logger.info(f"Engineered {len(df)} feature rows with {len(df.columns)} columns")
    return df


@task(name="store_features_task")
def store_features_task(features_df):
    """Store features in Feature Store"""
    logger.info("Storing features")
    success = store_features(features_df)
    logger.info(f"Feature storage {'successful' if success else 'failed'}")
    return success


@flow(name="feature_pipeline")
def feature_pipeline(hours: int = 24):
    """
    Main feature pipeline flow.
    
    1. Fetch price data from CoinGecko
    2. Engineer technical indicators and features
    3. Store in Hopsworks Feature Store
    """
    logger.info("=== Starting Feature Pipeline ===")
    start_time = datetime.now()
    
    # Fetch data
    price_data = fetch_price_data(hours)
    
    # Engineer features
    features_df = engineer_features_task(price_data)
    
    # Store features
    success = store_features_task(features_df)
    
    duration = (datetime.now() - start_time).total_seconds()
    logger.info(f"=== Feature Pipeline Complete ({duration:.2f}s) ===")
    
    return {
        "success": success,
        "rows_processed": len(features_df),
        "duration_seconds": duration,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    result = feature_pipeline()
    print(result)

