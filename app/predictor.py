"""Predictor - Load models and generate predictions with validation"""
import logging
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
    
    # Try loading from local directory first
    if model_loader.load():
        return True
    
    # If local load failed, try loading from Hopsworks Model Registry
    logger.info("Local models not found, attempting to load from Hopsworks...")
    try:
        from storage.model_registry import get_latest_model
        
        hw_model_data = get_latest_model()
        if hw_model_data and hw_model_data.get("models"):
            # Load models from Hopsworks data
            model_loader.models = hw_model_data.get("models", {})
            model_loader.scaler = hw_model_data.get("scaler")
            model_loader.metadata = hw_model_data.get("metadata", {})
            model_loader._loaded = bool(model_loader.models)
            
            if model_loader._loaded:
                logger.info(f"✅ Loaded {len(model_loader.models)} models from Hopsworks Model Registry")
                return True
    except Exception as e:
        logger.warning(f"Failed to load from Hopsworks: {e}")
    
    logger.error("❌ Could not load models from local or Hopsworks")
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
        
        # Get predictions from each regression model
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
        
        # Use best model prediction
        predicted_price = predictions.get(best_model, list(predictions.values())[0])
        
        # Direction from classifier if available
        if "classifier" in model_loader.models:
            direction_pred = model_loader.models["classifier"].predict(X_scaled)[0]
            direction = "up" if direction_pred == 1 else "down"
            direction_proba = model_loader.models["classifier"].predict_proba(X_scaled)
            confidence = float(max(direction_proba[0])) * 100
        else:
            direction = "up" if predicted_price > current_price else "down"
            confidence = min(95, 50 + abs(predicted_price - current_price) / current_price * 1000)
        
        # Market regime from K-Means if available
        regime = "neutral"
        if "kmeans" in model_loader.models and "pca" in model_loader.models:
            X_pca = model_loader.models["pca"].transform(X_scaled)
            cluster = model_loader.models["kmeans"].predict(X_pca)[0]
            regimes = ["accumulation", "uptrend", "distribution", "downtrend"]
            regime = regimes[cluster % len(regimes)]
        
        result = {
            "timestamp": datetime.now().isoformat(),
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


def validate_predictions(current_price: float):
    """Validate past predictions with tolerance-based correctness"""
    now = datetime.now()
    tolerance_pct = settings.DIRECTION_TOLERANCE_PCT
    
    for entry in prediction_history:
        if entry["was_correct"] is not None:
            continue
        
        pred_time = datetime.fromisoformat(entry["timestamp"])
        if now - pred_time < timedelta(minutes=settings.PREDICTION_MINUTES):
            continue
        
        entry["actual_price"] = round(current_price, 2)
        entry["validated_at"] = now.isoformat()
        
        price_at_prediction = entry["current_price"]
        predicted_direction = entry["predicted_direction"]
        
        # Calculate actual change
        actual_change = current_price - price_at_prediction
        actual_change_pct = abs(actual_change / price_at_prediction * 100)
        
        entry["error_amount"] = round(
            abs(entry["predicted_price"] - current_price), 2
        )
        
        # TOLERANCE-BASED VALIDATION
        # If price moved less than tolerance, consider it "neutral" - mark as incorrect
        # This prevents marking sideways movements as correct predictions
        if actual_change_pct < tolerance_pct:
            entry["was_correct"] = False
            entry["validation_note"] = "price_within_tolerance"
        else:
            actual_direction = "up" if actual_change > 0 else "down"
            entry["was_correct"] = (actual_direction == predicted_direction)
            entry["validation_note"] = "direction_validated"
        
        logger.info(
            f"Validated prediction: predicted={predicted_direction}, "
            f"actual_change={actual_change_pct:.2f}%, correct={entry['was_correct']}"
        )


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

