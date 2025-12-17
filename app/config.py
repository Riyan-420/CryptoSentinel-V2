"""CryptoSentinel Configuration - Python 3.11 Compatible"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Data
    SYMBOL: str = "BTCUSDT"
    HISTORY_HOURS: int = 24
    PREDICTION_MINUTES: int = 30
    TRAINING_INTERVAL_MINUTES: int = 30
    PREDICTION_REFRESH_MINUTES: int = 5
    
    # Validation tolerance (percentage)
    DIRECTION_TOLERANCE_PCT: float = 0.1
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent
    MODEL_DIR: Path = BASE_DIR / "models" / "saved"
    ACTIVE_MODEL_DIR: Path = BASE_DIR / "models" / "active"
    
    # Technical Indicators
    RSI_PERIOD: int = 14
    MACD_FAST: int = 12
    MACD_SLOW: int = 26
    MACD_SIGNAL: int = 9
    N_CLUSTERS: int = 4
    DRIFT_THRESHOLD: float = 0.3
    
    # Hardware
    USE_GPU: bool = os.getenv("USE_GPU", "false").lower() == "true"
    N_THREADS: int = int(os.getenv("OMP_NUM_THREADS", "4"))
    
    # Hopsworks
    HOPSWORKS_API_KEY: str = os.getenv("HOPSWORKS_API_KEY", "")
    HOPSWORKS_PROJECT_NAME: str = os.getenv("HOPSWORKS_PROJECT_NAME", "CryptoSentinel")
    
    # Notifications
    DISCORD_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")
    SLACK_WEBHOOK_URL: str = os.getenv("SLACK_WEBHOOK_URL", "")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()

# Create directories
settings.MODEL_DIR.mkdir(parents=True, exist_ok=True)
settings.ACTIVE_MODEL_DIR.mkdir(parents=True, exist_ok=True)

