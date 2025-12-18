"""Hopsworks Model Registry Integration"""
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import joblib

from app.config import settings

logger = logging.getLogger(__name__)

# Connection cache
_connection = None
_model_registry = None


def _connect():
    """Connect to Hopsworks Model Registry"""
    global _connection, _model_registry
    
    if _model_registry is not None:
        return _model_registry
    
    try:
        import hopsworks
        
        # Project-specific API keys don't need project parameter
        _connection = hopsworks.login(
            api_key_value=settings.HOPSWORKS_API_KEY
        )
        _model_registry = _connection.get_model_registry()
        logger.info(f"Connected to Hopsworks Model Registry (Project: {_connection.name})")
        return _model_registry
        
    except Exception as e:
        logger.error(f"Hopsworks connection failed: {e}")
        return None


def register_model(model: Any,
                   model_name: str = "crypto_price_predictor",
                   metrics: Dict[str, float] = None,
                   description: str = "Bitcoin price prediction model"
                  ) -> Optional[Any]:
    """Register a model in Hopsworks"""
    mr = _connect()
    
    if mr is None:
        logger.warning("Model Registry unavailable, saving locally only")
        return None
    
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # Save model to temp directory
            model_path = tmp_path / "model.joblib"
            joblib.dump(model, model_path)
            
            # Create model in registry
            hw_model = mr.python.create_model(
                name=model_name,
                metrics=metrics or {},
                description=description,
                input_example=None
            )
            
            # Upload model files
            hw_model.save(str(tmp_path))
            
            logger.info(f"Model '{model_name}' registered in Hopsworks (v{hw_model.version})")
            return hw_model
            
    except Exception as e:
        logger.error(f"Model registration error: {e}")
        return None


def register_model_bundle(models: Dict[str, Any],
                          scaler: Any,
                          metadata: Dict[str, Any],
                          model_name: str = "crypto_model_bundle"
                         ) -> Optional[Any]:
    """Register multiple models as a bundle"""
    mr = _connect()
    
    if mr is None:
        return None
    
    try:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            
            # Save all models
            for name, model in models.items():
                joblib.dump(model, tmp_path / f"{name}.joblib")
            
            # Save scaler
            joblib.dump(scaler, tmp_path / "scaler.joblib")
            
            # Save metadata
            joblib.dump(metadata, tmp_path / "metadata.joblib")
            
            # Create and upload
            metrics = metadata.get("metrics", {})
            hw_model = mr.python.create_model(
                name=model_name,
                metrics=metrics,
                description="CryptoSentinel model bundle with scaler and metadata"
            )
            hw_model.save(str(tmp_path))
            
            logger.info(f"Model bundle registered (v{hw_model.version})")
            return hw_model
            
    except Exception as e:
        logger.error(f"Model bundle registration error: {e}")
        return None


def get_latest_model(model_name: str = "crypto_model_bundle"
                    ) -> Optional[Dict[str, Any]]:
    """Get latest model from registry"""
    mr = _connect()
    
    if mr is None:
        return _load_model_locally()
    
    try:
        # Get latest version
        model = mr.get_model(model_name, version=None)
        
        with tempfile.TemporaryDirectory() as tmp_dir:
            model_dir = model.download(tmp_dir)
            model_path = Path(model_dir)
            
            result = {"models": {}, "scaler": None, "metadata": {}}
            
            for file in model_path.glob("*.joblib"):
                if file.stem == "scaler":
                    result["scaler"] = joblib.load(file)
                elif file.stem == "metadata":
                    result["metadata"] = joblib.load(file)
                else:
                    result["models"][file.stem] = joblib.load(file)
            
            logger.info(f"Loaded model {model_name} v{model.version}")
            return result
            
    except Exception as e:
        logger.error(f"Model fetch error: {e}")
        return _load_model_locally()


def list_model_versions(model_name: str = "crypto_model_bundle"
                       ) -> List[Dict[str, Any]]:
    """List all versions of a model"""
    mr = _connect()
    
    if mr is None:
        return []
    
    try:
        models = mr.get_models(model_name)
        return [
            {
                "version": m.version,
                "created": m.created,
                "metrics": m.training_metrics
            }
            for m in models
        ]
    except Exception as e:
        logger.error(f"Model listing error: {e}")
        return []


def _load_model_locally() -> Optional[Dict[str, Any]]:
    """Fallback: Load model from local storage"""
    try:
        model_dir = settings.ACTIVE_MODEL_DIR
        if not model_dir.exists():
            return None
        
        result = {"models": {}, "scaler": None, "metadata": {}}
        
        for file in model_dir.glob("*.joblib"):
            if file.stem == "scaler":
                result["scaler"] = joblib.load(file)
            elif file.stem == "metadata":
                result["metadata"] = joblib.load(file)
            else:
                result["models"][file.stem] = joblib.load(file)
        
        if result["models"]:
            logger.info("Loaded models from local storage")
            return result
        return None
        
    except Exception as e:
        logger.error(f"Local model load error: {e}")
        return None

