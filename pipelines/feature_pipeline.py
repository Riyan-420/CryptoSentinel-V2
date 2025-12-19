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
def feature_pipeline(hours: int = None):
    """
    Main feature pipeline flow.
    
    1. Fetch price data from CoinGecko
    2. Engineer technical indicators and features
    3. Store in Hopsworks Feature Store
    
    Smart default behavior:
    - If Feature Store is empty: Fetch 72 hours (3 days) for initial training data
    - If Feature Store has data: Fetch 2 hours (recent data only)
    
    This ensures:
    - Initial setup has enough historical data for model training
    - Regular runs only fetch fresh data (efficient)
    - No manual intervention needed
    """
    logger.info("=== Starting Feature Pipeline ===")
    start_time = datetime.now()
    
    # Smart hour selection if not specified
    if hours is None:
        from storage.feature_store import get_or_create_feature_group
        fg = get_or_create_feature_group()
        
        try:
            existing_data = fg.read(limit=1) if fg else None
            if existing_data is None or len(existing_data) == 0:
                hours = 72  # Initial run: 3 days (enough for training, not too much)
                logger.info("Feature Store empty - fetching 72 hours (3 days) for initial setup")
            else:
                hours = 2  # Regular run: 2 hours for fresh data only
                logger.info("Feature Store has data - fetching 2 hours for updates")
        except:
            hours = 2  # Default to 2 hours if check fails
            logger.info("Using default 2 hours")
    
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

