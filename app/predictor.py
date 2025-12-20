"""Predictor - Load models and generate predictions with validation"""
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import deque

import numpy as np
import pandas as pd
import joblib

from app.config import settings
from app.feature_engineering import get_feature_names

logger = logging.getLogger(__name__)

try:
    from zoneinfo import ZoneInfo
    GMT_PLUS_5 = ZoneInfo("Asia/Karachi")
except ImportError:
    try:
        import pytz
        GMT_PLUS_5 = pytz.timezone("Asia/Karachi")
    except ImportError:
        GMT_PLUS_5 = None
        logger.warning("No timezone library available, using system timezone")

PREDICTIONS_FILE = Path(settings.BASE_DIR) / "data" / "predictions_history.json"
PREDICTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)

# Prediction history buffer (in-memory, max 50 entries)
prediction_history: deque = deque(maxlen=50)


class ModelLoader:
    """Handles loading and managing trained models"""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.scaler = None
        self.metadata: Dict[str, Any] = {}
        self._loaded = False
    
    def load(self, model_dir: Optional[Path] = None) -> bool:
        """Load all models from directory"""
        if model_dir is None:
            model_dir = settings.ACTIVE_MODEL_DIR
        
        if not model_dir.exists():
            logger.warning(f"Model directory not found: {model_dir}")
            return False
        
        try:
            # Load metadata
            metadata_path = model_dir / "metadata.joblib"
            if metadata_path.exists():
                self.metadata = joblib.load(metadata_path)
            
            # Load scaler
            scaler_path = model_dir / "scaler.joblib"
            if scaler_path.exists():
                self.scaler = joblib.load(scaler_path)
            
            # Load all models
            for model_file in model_dir.glob("*.joblib"):
                if model_file.stem not in ["metadata", "scaler"]:
                    self.models[model_file.stem] = joblib.load(model_file)
            
            self._loaded = bool(self.models)
            logger.info(f"Loaded {len(self.models)} models from {model_dir}")
            return self._loaded
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
    
    @property
    def is_loaded(self) -> bool:
        return self._loaded
    
    @property
    def best_model_name(self) -> str:
        return self.metadata.get("best_model", "xgboost")


# Global model loader
model_loader = ModelLoader()


def ensure_models_loaded() -> bool:
    """Ensure models are loaded - try local first, then Hopsworks"""
    if model_loader.is_loaded:
        return True
    
    if model_loader.load():
        return True
    logger.info("Local models not found, attempting to load from Hopsworks...")
    try:
        from storage.model_registry import get_latest_model
        
        hw_model_data = get_latest_model()
        if hw_model_data and hw_model_data.get("models"):
            model_loader.models = hw_model_data.get("models", {})
            model_loader.scaler = hw_model_data.get("scaler")
            model_loader.metadata = hw_model_data.get("metadata", {})
            model_loader._loaded = bool(model_loader.models)
            
            if model_loader._loaded:
                logger.info(f"Loaded {len(model_loader.models)} models from Hopsworks Model Registry")
                return True
    except Exception as e:
        logger.warning(f"Failed to load from Hopsworks: {e}")
    
    logger.error("Could not load models from local or Hopsworks")
    return False


def generate_prediction(features: pd.DataFrame, current_price: float
                       ) -> Optional[Dict[str, Any]]:
    """Generate predictions using all models"""
    if not ensure_models_loaded():
        logger.warning("Models not loaded, cannot predict")
        return None
    
    try:
        feature_cols = get_feature_names()
        X = features[feature_cols].iloc[-1:].copy()
        
        if model_loader.scaler:
            X_scaled = model_loader.scaler.transform(X)
        else:
            X_scaled = X.values
        
        predictions = {}
        best_model = model_loader.best_model_name
        
        for name, model in model_loader.models.items():
            if name in ["classifier", "kmeans", "pca"]:
                continue
            try:
                pred = float(model.predict(X_scaled)[0])
                predictions[name] = pred
            except Exception as e:
                logger.error(f"Prediction error for {name}: {e}")
        
        if not predictions:
            return None
        
        predicted_price = predictions.get(best_model, list(predictions.values())[0])
        
        direction = "up" if predicted_price > current_price else "down"
        price_diff_pct = abs(predicted_price - current_price) / current_price * 100
        confidence = min(95, 50 + price_diff_pct * 10)
        if "classifier" in model_loader.models:
            try:
                classifier_pred = model_loader.models["classifier"].predict(X_scaled)[0]
                classifier_direction = "up" if classifier_pred == 1 else "down"
                direction_proba = model_loader.models["classifier"].predict_proba(X_scaled)
                classifier_confidence = float(max(direction_proba[0])) * 100
                
                if classifier_direction != direction:
                    logger.warning(
                        f"Classifier disagrees with price prediction: "
                        f"price says {direction} (${predicted_price:.2f} vs ${current_price:.2f}), "
                        f"classifier says {classifier_direction} ({classifier_confidence:.1f}% confidence)"
                    )
                
                if classifier_direction == direction and classifier_confidence > confidence:
                    confidence = classifier_confidence
            except Exception as e:
                logger.warning(f"Classifier prediction failed: {e}, using price-based direction")
        
        regime = "neutral"
        if "kmeans" in model_loader.models and "pca" in model_loader.models:
            X_pca = model_loader.models["pca"].transform(X_scaled)
            cluster = model_loader.models["kmeans"].predict(X_pca)[0]
            regimes = ["accumulation", "uptrend", "distribution", "downtrend"]
            regime = regimes[cluster % len(regimes)]
        
        prediction_time = datetime.now()
        target_time = prediction_time + timedelta(minutes=settings.PREDICTION_MINUTES)
        
        result = {
            "timestamp": prediction_time.isoformat(),
            "target_timestamp": target_time.isoformat(),
            "target_timestamp_ms": int(target_time.timestamp() * 1000),
            "current_price": round(current_price, 2),
            "predicted_price": round(predicted_price, 2),
            "predicted_direction": direction,
            "confidence": round(confidence, 1),
            "price_change": round(predicted_price - current_price, 2),
            "price_change_pct": round((predicted_price - current_price) / current_price * 100, 2),
            "market_regime": regime,
            "model_used": best_model,
            "all_predictions": {k: round(v, 2) for k, v in predictions.items()},
            "prediction_horizon_minutes": settings.PREDICTION_MINUTES
        }
        
        # Store in history
        _store_prediction(result)
        
        return result
        
    except Exception as e:
        logger.error(f"Prediction generation error: {e}")
        return None


def _store_prediction(prediction: Dict[str, Any]):
    """Store prediction in history"""
    entry = {
        **prediction,
        "actual_price": None,
        "was_correct": None,
        "error_amount": None,
        "validated_at": None
    }
    prediction_history.append(entry)
    _save_predictions_to_file()


def _save_predictions_to_file():
    """Save predictions to JSON file and sync to Hopsworks"""
    try:
        data = list(prediction_history)
        with open(PREDICTIONS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save predictions to file: {e}")
    
    try:
        from storage.prediction_store import sync_predictions_to_hopsworks
        sync_predictions_to_hopsworks(list(prediction_history))
    except Exception as e:
        logger.warning(f"Failed to sync predictions to Hopsworks: {e}")


def _load_predictions_from_file():
    """Load predictions from JSON file and Hopsworks on startup"""
    global prediction_history
    
    loaded_from_hopsworks = False
    try:
        from storage.prediction_store import fetch_predictions_from_hopsworks
        hopsworks_predictions = fetch_predictions_from_hopsworks(limit=50)
        if hopsworks_predictions:
            prediction_history.extend(hopsworks_predictions)
            logger.info(f"Loaded {len(hopsworks_predictions)} predictions from Hopsworks")
            loaded_from_hopsworks = True
    except Exception as e:
        logger.warning(f"Could not load predictions from Hopsworks: {e}")
    
    if not loaded_from_hopsworks:
        try:
            if PREDICTIONS_FILE.exists():
                with open(PREDICTIONS_FILE, 'r') as f:
                    data = json.load(f)
                    prediction_history.extend(data[-50:])
                logger.info(f"Loaded {len(data)} predictions from local file")
        except Exception as e:
            logger.error(f"Failed to load predictions from file: {e}")


def validate_predictions(current_price: float = None):
    """Validate past predictions by checking if we have data for their target time"""
    from app.data_fetcher import fetch_price_history
    
    tolerance_pct = settings.DIRECTION_TOLERANCE_PCT
    now = datetime.now()
    
    # Fetch recent price history to check target times
    try:
        history_hours = max(2, settings.PREDICTION_MINUTES / 60 + 1)
        price_history = fetch_price_history(hours=int(history_hours))
        price_dict = {p["timestamp"]: p["price"] for p in price_history}
    except Exception as e:
        logger.warning(f"Could not fetch price history for validation: {e}")
        if current_price is None:
            return
        price_dict = {}
    
    for entry in prediction_history:
        if entry["was_correct"] is not None:
            continue
        
        target_timestamp_ms = entry.get("target_timestamp_ms")
        if not target_timestamp_ms:
            try:
                pred_time = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    pred_time = datetime.fromisoformat(entry["timestamp"])
                except:
                    continue
            pred_time = pred_time.replace(tzinfo=None) if pred_time.tzinfo else pred_time
            target_time = pred_time + timedelta(minutes=settings.PREDICTION_MINUTES)
            target_timestamp_ms = int(target_time.timestamp() * 1000)
        
        actual_price = None
        for hist_ts, hist_price in price_dict.items():
            time_diff_ms = abs(hist_ts - target_timestamp_ms)
            if time_diff_ms <= 5 * 60 * 1000:
                actual_price = hist_price
                break
        
        if actual_price is None:
            target_time = datetime.fromtimestamp(target_timestamp_ms / 1000)
            if now >= target_time:
                if current_price is not None:
                    actual_price = current_price
                else:
                    continue
            else:
                continue
        
        entry["actual_price"] = round(actual_price, 2)
        entry["validated_at"] = now.isoformat()
        
        price_at_prediction = entry["current_price"]
        predicted_direction = entry["predicted_direction"]
        predicted_price = entry["predicted_price"]
        actual_change = actual_price - price_at_prediction
        actual_change_pct = abs(actual_change / price_at_prediction * 100)
        
        entry["error_amount"] = round(abs(predicted_price - actual_price), 2)
        
        if actual_change_pct < tolerance_pct:
            entry["was_correct"] = False
            entry["validation_note"] = "price_within_tolerance"
        else:
            actual_direction = "up" if actual_change > 0 else "down"
            entry["was_correct"] = (actual_direction == predicted_direction)
            entry["validation_note"] = "direction_validated"
        
        logger.info(
            f"Validated prediction from {entry['timestamp'][:19]}: "
            f"predicted={predicted_direction} to ${predicted_price:,.2f}, "
            f"actual at target time=${actual_price:,.2f}, "
            f"change={actual_change_pct:.2f}%, correct={entry['was_correct']}"
        )
    
    _save_predictions_to_file()


def get_prediction_history() -> List[Dict[str, Any]]:
    """Get prediction history as list"""
    return list(prediction_history)


def get_prediction_accuracy() -> Dict[str, Any]:
    """Calculate prediction accuracy statistics"""
    validated = [p for p in prediction_history if p["was_correct"] is not None]
    
    if not validated:
        return {"accuracy": 0, "total_predictions": 0, "validated_count": 0}
    
    correct = sum(1 for p in validated if p["was_correct"])
    
    return {
        "accuracy": round(correct / len(validated) * 100, 1),
        "total_predictions": len(prediction_history),
        "validated_count": len(validated),
        "correct_count": correct,
        "avg_error": round(
            np.mean([p["error_amount"] for p in validated if p["error_amount"]]), 2
        )
    }


# Load predictions from file on module initialization
try:
    if PREDICTIONS_FILE.exists():
        with open(PREDICTIONS_FILE, 'r') as f:
            data = json.load(f)
            prediction_history.extend(data[-50:])
        logger.info(f"Loaded {len(data)} predictions from file on startup")
except Exception as e:
    logger.error(f"Failed to load predictions on startup: {e}")
