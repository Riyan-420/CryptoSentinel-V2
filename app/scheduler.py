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
    except Exception as e:
        logger.error(f"Training pipeline error: {e}")


def _scheduler_loop():
    """Main scheduler loop"""
    global _scheduler_running, _last_feature_run, _last_training_run
    
    feature_interval = settings.PREDICTION_REFRESH_MINUTES * 60
    training_interval = settings.TRAINING_INTERVAL_MINUTES * 60
    
    last_feature_time = 0
    last_training_time = 0
    
    logger.info("Background scheduler started")
    logger.info(f"Feature pipeline: every {settings.PREDICTION_REFRESH_MINUTES} minutes")
    logger.info(f"Training pipeline: every {settings.TRAINING_INTERVAL_MINUTES} minutes")
    
    while _scheduler_running:
        current_time = time.time()
        
        if current_time - last_feature_time >= feature_interval:
            _run_feature_pipeline()
            last_feature_time = current_time
        
        if current_time - last_training_time >= training_interval:
            _run_training_pipeline()
            last_training_time = current_time
        
        time.sleep(60)


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
        "last_training_run": _last_training_run.isoformat() if _last_training_run else None
    }

