"""FastAPI Backend - CryptoSentinel API"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import settings
from api.routes import router
from pipelines.inference_pipeline import inference_pipeline
from pipelines.training_pipeline import training_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Scheduler for periodic predictions
scheduler = AsyncIOScheduler()


def run_scheduled_prediction():
    """Run prediction pipeline on schedule"""
    try:
        logger.info("Running scheduled prediction")
        result = inference_pipeline()
        logger.info(f"Prediction complete: {result.get('prediction', {}).get('predicted_price')}")
    except Exception as e:
        logger.error(f"Scheduled prediction error: {e}")


def run_scheduled_training():
    """Run training pipeline on schedule"""
    try:
        logger.info("Running scheduled training")
        result = training_pipeline()
        logger.info(f"Training complete: Best model = {result.get('best_model', 'N/A')}")
    except Exception as e:
        logger.error(f"Scheduled training error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("CryptoSentinel API starting up")
    
    # Load models
    from app.predictor import model_loader
    loaded = model_loader.load()
    if loaded:
        logger.info("Models loaded successfully")
    else:
        logger.warning("No models loaded - run training pipeline first")
    
    # Start schedulers
    # Inference pipeline - every 5 minutes
    scheduler.add_job(
        run_scheduled_prediction,
        "interval",
        minutes=settings.PREDICTION_REFRESH_MINUTES,
        id="prediction_job",
        next_run_time=datetime.now()
    )
    
    # Training pipeline - every 30 minutes
    scheduler.add_job(
        run_scheduled_training,
        "interval",
        minutes=settings.TRAINING_INTERVAL_MINUTES,
        id="training_job",
        next_run_time=datetime.now()
    )
    
    scheduler.start()
    logger.info(f"Scheduler started:")
    logger.info(f"  - Inference pipeline: every {settings.PREDICTION_REFRESH_MINUTES} min")
    logger.info(f"  - Training pipeline: every {settings.TRAINING_INTERVAL_MINUTES} min")
    
    yield
    
    # Shutdown
    scheduler.shutdown()
    logger.info("CryptoSentinel API shutting down")


app = FastAPI(
    title="CryptoSentinel API",
    description="Bitcoin Price Prediction with ML",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Include routes
app.include_router(router, prefix="/api")


@app.get("/")
def root():
    """Health check"""
    return {
        "status": "healthy",
        "service": "CryptoSentinel API",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    from app.predictor import model_loader
    
    return {
        "status": "healthy",
        "models_loaded": model_loader.is_loaded,
        "best_model": model_loader.best_model_name if model_loader.is_loaded else None,
        "scheduler_running": scheduler.running,
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )

