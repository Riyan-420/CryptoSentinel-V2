"""Hopsworks Feature Store Integration"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

# Connection cache
_connection = None
_feature_store = None


def _connect():
    """Connect to Hopsworks Feature Store"""
    global _connection, _feature_store
    
    if _feature_store is not None:
        return _feature_store
    
    try:
        import hopsworks
        
        # Project-specific API keys don't need project parameter
        _connection = hopsworks.login(
            api_key_value=settings.HOPSWORKS_API_KEY
        )
        _feature_store = _connection.get_feature_store()
        logger.info(f"Connected to Hopsworks Feature Store (Project: {_connection.name})")
        return _feature_store
        
    except Exception as e:
        logger.error(f"Hopsworks connection failed: {e}")
        return None


def get_or_create_feature_group(name: str = "crypto_features",
                                 version: int = 1,
                                 primary_key: list = None,
                                 description: str = "Bitcoin price features"
                                ) -> Optional[Any]:
    """Get or create a feature group"""
    fs = _connect()
    if fs is None:
        return None
    
    try:
        if primary_key is None:
            primary_key = ["timestamp"]
        
        fg = fs.get_or_create_feature_group(
            name=name,
            version=version,
            primary_key=primary_key,
            description=description,
            online_enabled=True
        )
        return fg
        
    except Exception as e:
        logger.error(f"Feature group error: {e}")
        return None


def store_features(df: pd.DataFrame, 
                   feature_group_name: str = "crypto_features") -> bool:
    """Store features in Hopsworks"""
    fg = get_or_create_feature_group(feature_group_name)
    
    if fg is None:
        logger.warning("Feature group unavailable, saving locally")
        return _save_features_locally(df)
    
    try:
        # Ensure timestamp column exists
        if 'timestamp' not in df.columns:
            df = df.reset_index()
            df.rename(columns={'index': 'timestamp'}, inplace=True)
        
        # Convert timestamp to string for Hopsworks
        if pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            df['timestamp'] = df['timestamp'].astype(str)
        
        fg.insert(df)
        logger.info(f"Stored {len(df)} rows in Feature Store")
        return True
        
    except Exception as e:
        logger.error(f"Feature store insert error: {e}")
        return _save_features_locally(df)


def fetch_features(feature_group_name: str = "crypto_features",
                   limit: int = 1000) -> Optional[pd.DataFrame]:
    """Fetch features from Hopsworks"""
    fg = get_or_create_feature_group(feature_group_name)
    
    if fg is None:
        return _load_features_locally()
    
    try:
        df = fg.read()
        logger.info(f"Fetched {len(df)} rows from Feature Store")
        return df.tail(limit) if len(df) > limit else df
        
    except Exception as e:
        logger.error(f"Feature store fetch error: {e}")
        return _load_features_locally()


def get_latest_features(feature_group_name: str = "crypto_features",
                        n: int = 100) -> Optional[pd.DataFrame]:
    """Get latest N feature rows"""
    df = fetch_features(feature_group_name)
    if df is not None and len(df) > n:
        return df.tail(n)
    return df


def _save_features_locally(df: pd.DataFrame) -> bool:
    """Fallback: Save features locally"""
    try:
        local_path = settings.BASE_DIR / "data" / "features.parquet"
        local_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_parquet(local_path)
        logger.info(f"Features saved locally to {local_path}")
        return True
    except Exception as e:
        logger.error(f"Local save error: {e}")
        return False


def _load_features_locally() -> Optional[pd.DataFrame]:
    """Fallback: Load features from local storage"""
    try:
        local_path = settings.BASE_DIR / "data" / "features.parquet"
        if local_path.exists():
            return pd.read_parquet(local_path)
        return None
    except Exception as e:
        logger.error(f"Local load error: {e}")
        return None

