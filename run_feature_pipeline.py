"""Direct execution of feature pipeline (for GitHub Actions)"""
import logging
import sys
from datetime import datetime

from app.data_fetcher import fetch_price_history
from app.feature_engineering import engineer_features
from storage.feature_store import store_features

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run feature pipeline directly (without Prefect)"""
    logger.info("=== Starting Feature Pipeline (Direct Execution) ===")
    start_time = datetime.now()
    
    try:
        # Fetch data
        logger.info("Fetching price data...")
        price_data = fetch_price_history(hours=24)
        logger.info(f"Fetched {len(price_data)} price points")
        
        # Engineer features
        logger.info("Engineering features...")
        features_df = engineer_features(price_data)
        logger.info(f"Engineered {len(features_df)} feature rows with {len(features_df.columns)} columns")
        
        # Store features
        logger.info("Storing features in Hopsworks...")
        success = store_features(features_df)
        
        duration = (datetime.now() - start_time).total_seconds()
        
        if success:
            logger.info(f"✅ Feature Pipeline Complete ({duration:.2f}s)")
            logger.info(f"Stored {len(features_df)} rows in Feature Store")
            return 0
        else:
            logger.error("❌ Feature Pipeline Failed - Could not store features")
            return 1
            
    except Exception as e:
        logger.error(f"❌ Feature Pipeline Error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())

