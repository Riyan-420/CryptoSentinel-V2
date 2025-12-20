"""Prediction storage in Hopsworks Feature Store"""
import logging
from typing import List, Dict, Any
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)


def get_prediction_feature_group():
    """Get or create prediction history feature group"""
    try:
        from storage.feature_store import _connect
        
        project = _connect()
        if project is None:
            return None
        
        fs = project.get_feature_store()
        
        try:
            fg = fs.get_feature_group("prediction_history", version=1)
            logger.info("Retrieved existing prediction_history feature group")
        except:
            logger.info("Creating new prediction_history feature group")
            fg = fs.create_feature_group(
                name="prediction_history",
                version=1,
                primary_key=["timestamp"],
                description="Bitcoin price prediction history with validation",
                online_enabled=True
            )
        
        return fg
        
    except Exception as e:
        logger.error(f"Failed to get prediction feature group: {e}")
        return None


def store_predictions_to_hopsworks(predictions: List[Dict[str, Any]]):
    """Store predictions in Hopsworks Feature Store"""
    try:
        if not predictions:
            return False
        
        fg = get_prediction_feature_group()
        if fg is None:
            logger.warning("Prediction feature group not available, using local storage")
            return False
        
        df = pd.DataFrame(predictions)
        
        required_cols = [
            "timestamp", "target_timestamp", "current_price", "predicted_price",
            "predicted_direction", "confidence", "market_regime", "model_used"
        ]
        
        optional_cols = [
            "actual_price", "was_correct", "error_amount", "validated_at",
            "price_change", "price_change_pct"
        ]
        
        for col in optional_cols:
            if col not in df.columns:
                df[col] = None
        
        available_cols = [c for c in required_cols + optional_cols if c in df.columns]
        df = df[available_cols]
        
        existing_data = fg.read()
        if not existing_data.empty:
            existing_timestamps = set(existing_data['timestamp'].values)
            df = df[~df['timestamp'].isin(existing_timestamps)]
        
        if df.empty:
            logger.info("No new predictions to store")
            return True
        
        fg.insert(df, write_options={"wait_for_job": False})
        logger.info(f"Stored {len(df)} predictions to Hopsworks")
        return True
        
    except Exception as e:
        logger.error(f"Failed to store predictions to Hopsworks: {e}")
        return False


def fetch_predictions_from_hopsworks(limit: int = 50, hours: int = 2) -> List[Dict[str, Any]]:
    """Fetch predictions from Hopsworks Feature Store"""
    try:
        fg = get_prediction_feature_group()
        if fg is None:
            return []
        
        df = fg.read()
        
        if df.empty:
            return []
        
        # Only fetch predictions from the last X hours
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        cutoff_time = pd.Timestamp.now() - pd.Timedelta(hours=hours)
        df = df[df['timestamp'] >= cutoff_time]
        
        df = df.sort_values('timestamp', ascending=False).head(limit)
        
        predictions = df.to_dict('records')
        logger.info(f"Fetched {len(predictions)} predictions from Hopsworks (last {hours}h)")
        return predictions
        
    except Exception as e:
        logger.error(f"Failed to fetch predictions from Hopsworks: {e}")
        return []


def clear_prediction_history():
    """Clear all predictions from Hopsworks and local storage"""
    try:
        # Clear Hopsworks feature group by deleting and recreating
        from storage.feature_store import _connect
        
        project = _connect()
        if project:
            fs = project.get_feature_store()
            try:
                fg = fs.get_feature_group("prediction_history", version=1)
                fg.delete()
                logger.info("Deleted prediction_history feature group from Hopsworks")
            except Exception as e:
                logger.info(f"No existing prediction_history to delete: {e}")
        
        # Clear local file
        from app.config import settings
        predictions_file = Path(settings.BASE_DIR) / "data" / "predictions_history.json"
        if predictions_file.exists():
            predictions_file.unlink()
            logger.info("Deleted local predictions file")
        
        logger.info("Prediction history cleared successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to clear prediction history: {e}")
        return False


def sync_predictions_to_hopsworks(predictions: List[Dict[str, Any]]):
    """Sync current predictions to Hopsworks (called periodically)"""
    if not predictions:
        return
    
    try:
        store_predictions_to_hopsworks(predictions)
    except Exception as e:
        logger.error(f"Prediction sync error: {e}")

