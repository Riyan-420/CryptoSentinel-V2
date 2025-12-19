"""Background scheduler for pipelines in Streamlit"""
import threading
import time
import logging
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)

_scheduler_thread = None
_scheduler_running = False
_last_feature_run = None
_last_training_run = None
_last_inference_run = None


def _run_feature_pipeline():
    """Run feature pipeline"""
    global _last_feature_run
    try:
        logger.info("Running scheduled feature pipeline")
        from pipelines.feature_pipeline import feature_pipeline
        result = feature_pipeline()
        _last_feature_run = datetime.now()
        logger.info(f"Feature pipeline complete: {result.get('success', False)}")
    except Exception as e:
        logger.error(f"Feature pipeline error: {e}")


def _run_training_pipeline():
    """Run training pipeline"""
    global _last_training_run
    try:
        logger.info("Running scheduled training pipeline")
        from pipelines.training_pipeline import training_pipeline
        result = training_pipeline()
        _last_training_run = datetime.now()
        logger.info(f"Training pipeline complete: Best model = {result.get('best_model', 'N/A')}")
        _reload_models()
    except Exception as e:
        logger.error(f"Training pipeline error: {e}")


def _run_inference_pipeline():
    """Run inference pipeline"""
    global _last_inference_run
    try:
        logger.info("Running scheduled inference pipeline")
        from pipelines.inference_pipeline import inference_pipeline
        result = inference_pipeline()
        _last_inference_run = datetime.now()
        logger.info(f"Inference pipeline complete: {result.get('success', False)}")
    except Exception as e:
        logger.error(f"Inference pipeline error: {e}")


def _reload_models():
    """Force reload models from Hopsworks after training"""
    try:
        logger.info("Reloading models after training")
        from app.predictor import model_loader
        model_loader._loaded = False
        from storage.model_registry import get_latest_model
        hw_model_data = get_latest_model()
        if hw_model_data and hw_model_data.get("models"):
            model_loader.models = hw_model_data.get("models", {})
            model_loader.scaler = hw_model_data.get("scaler")
            model_loader.metadata = hw_model_data.get("metadata", {})
            model_loader._loaded = True
            logger.info(f"Reloaded {len(model_loader.models)} models from Hopsworks")
    except Exception as e:
        logger.error(f"Model reload error: {e}")


def _scheduler_loop():
    """Main scheduler loop"""
    global _scheduler_running, _last_feature_run, _last_training_run, _last_inference_run
    
    feature_interval = settings.PREDICTION_REFRESH_MINUTES * 60
    training_interval = settings.TRAINING_INTERVAL_MINUTES * 60
    inference_interval = settings.PREDICTION_REFRESH_MINUTES * 60
    
    last_feature_time = 0
    last_training_time = 0
    last_inference_time = 0
    
    logger.info("Background scheduler started")
    logger.info(f"Feature pipeline: every {settings.PREDICTION_REFRESH_MINUTES} minutes")
    logger.info(f"Training pipeline: every {settings.TRAINING_INTERVAL_MINUTES} minutes")
    logger.info(f"Inference pipeline: every {settings.PREDICTION_REFRESH_MINUTES} minutes")
    
    _run_inference_pipeline()
    last_inference_time = time.time()
    
    while _scheduler_running:
        current_time = time.time()
        
        if current_time - last_feature_time >= feature_interval:
            _run_feature_pipeline()
            last_feature_time = current_time
        
        if current_time - last_training_time >= training_interval:
            _run_training_pipeline()
            last_training_time = current_time
        
        if current_time - last_inference_time >= inference_interval:
            _run_inference_pipeline()
            last_inference_time = current_time
        
        time.sleep(30)


def start_scheduler():
    """Start background scheduler"""
    global _scheduler_thread, _scheduler_running
    
    if _scheduler_running:
        return
    
    _scheduler_running = True
    _scheduler_thread = threading.Thread(target=_scheduler_loop, daemon=True)
    _scheduler_thread.start()
    logger.info("Background scheduler thread started")


def stop_scheduler():
    """Stop background scheduler"""
    global _scheduler_running
    _scheduler_running = False
    logger.info("Background scheduler stopped")


def get_scheduler_status():
    """Get scheduler status"""
    return {
        "running": _scheduler_running,
        "last_feature_run": _last_feature_run.isoformat() if _last_feature_run else None,
        "last_training_run": _last_training_run.isoformat() if _last_training_run else None,
        "last_inference_run": _last_inference_run.isoformat() if _last_inference_run else None
    }

