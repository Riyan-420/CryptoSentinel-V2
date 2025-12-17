"""Model Training - Multiple Model Selection"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

import numpy as np
import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import Ridge
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from xgboost import XGBRegressor

from app.config import settings
from app.feature_engineering import get_feature_names

logger = logging.getLogger(__name__)

REGRESSION_MODELS = {
    "xgboost": XGBRegressor(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        n_jobs=-1,
        random_state=42
    ),
    "random_forest": RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        n_jobs=-1,
        random_state=42
    ),
    "gradient_boosting": GradientBoostingRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    ),
    "ridge": Ridge(alpha=1.0)
}


def train_regression_models(X: pd.DataFrame, y: pd.Series
                           ) -> Dict[str, Tuple[Any, Dict[str, float]]]:
    """Train multiple regression models and return with metrics"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    results = {}
    
    for name, model in REGRESSION_MODELS.items():
        try:
            model.fit(X_train_scaled, y_train)
            preds = model.predict(X_test_scaled)
            
            metrics = {
                "rmse": float(np.sqrt(mean_squared_error(y_test, preds))),
                "mae": float(mean_absolute_error(y_test, preds)),
                "r2": float(r2_score(y_test, preds))
            }
            
            results[name] = (model, metrics)
            logger.info(f"{name}: RMSE={metrics['rmse']:.2f}, R2={metrics['r2']:.4f}")
            
        except Exception as e:
            logger.error(f"Training {name} failed: {e}")
    
    return results, scaler


def train_classifier(X: pd.DataFrame, y: pd.Series
                    ) -> Tuple[GradientBoostingClassifier, Dict[str, float]]:
    """Train direction classifier"""
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )
    
    model = GradientBoostingClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42
    )
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    
    metrics = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "f1": float(f1_score(y_test, preds, zero_division=0))
    }
    
    logger.info(f"Classifier: Accuracy={metrics['accuracy']:.4f}")
    return model, metrics


def train_kmeans(X: pd.DataFrame, n_clusters: int = 4) -> Tuple[KMeans, PCA]:
    """Train K-Means for market regime detection"""
    pca = PCA(n_components=min(5, X.shape[1]))
    X_pca = pca.fit_transform(X)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(X_pca)
    
    logger.info(f"K-Means trained with {n_clusters} clusters")
    return kmeans, pca


def select_best_model(results: Dict[str, Tuple[Any, Dict[str, float]]]) -> str:
    """Select best model based on RMSE"""
    best_name = None
    best_rmse = float('inf')
    
    for name, (_, metrics) in results.items():
        if metrics["rmse"] < best_rmse:
            best_rmse = metrics["rmse"]
            best_name = name
    
    logger.info(f"Best model: {best_name} with RMSE={best_rmse:.4f}")
    return best_name


def save_models(models: Dict[str, Any], scaler: StandardScaler,
                best_model_name: str, version: Optional[str] = None) -> Path:
    """Save all models to disk"""
    if version is None:
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    save_dir = settings.MODEL_DIR / version
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Save individual models
    for name, model in models.items():
        joblib.dump(model, save_dir / f"{name}.joblib")
    
    # Save scaler
    joblib.dump(scaler, save_dir / "scaler.joblib")
    
    # Save metadata
    metadata = {
        "version": version,
        "best_model": best_model_name,
        "created_at": datetime.now().isoformat(),
        "feature_names": get_feature_names()
    }
    joblib.dump(metadata, save_dir / "metadata.joblib")
    
    logger.info(f"Models saved to {save_dir}")
    return save_dir


def promote_to_active(version_dir: Path):
    """Copy version to active directory"""
    import shutil
    
    # Clear active directory
    if settings.ACTIVE_MODEL_DIR.exists():
        shutil.rmtree(settings.ACTIVE_MODEL_DIR)
    
    # Copy new version
    shutil.copytree(version_dir, settings.ACTIVE_MODEL_DIR)
    logger.info(f"Promoted {version_dir.name} to active")

