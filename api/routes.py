"""API Routes - All endpoints"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.data_fetcher import fetch_current_price, fetch_price_history, fetch_market_data
from app.feature_engineering import engineer_features
from app.predictor import (
    generate_prediction, get_prediction_history, 
    get_prediction_accuracy, validate_predictions
)
from app.explainer import get_shap_values, get_feature_importance, get_model_explanation_summary
from app.drift_detection import get_drift_reports, get_drift_summary
from app.alerts import get_alert_history, get_alert_summary
from app.eda import generate_eda_report, identify_trend

logger = logging.getLogger(__name__)
router = APIRouter()


# Price endpoints
@router.get("/price/current")
def get_current_price():
    """Get current Bitcoin price"""
    try:
        return fetch_current_price()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/history")
def get_price_history(hours: int = Query(24, ge=1, le=168)):
    """Get price history"""
    try:
        return fetch_price_history(hours)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/price/market")
def get_market():
    """Get market data"""
    try:
        return fetch_market_data()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Prediction endpoints
@router.get("/prediction/current")
def get_current_prediction():
    """Get current prediction"""
    try:
        current = fetch_current_price()
        history = fetch_price_history(hours=6)
        features = engineer_features(history)
        prediction = generate_prediction(features, current["current_price"])
        
        if prediction is None:
            raise HTTPException(status_code=503, detail="Models not loaded")
        
        return prediction
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prediction/history")
def get_predictions_history(limit: int = Query(20, ge=1, le=100)):
    """Get prediction history"""
    history = get_prediction_history()
    return history[-limit:]


@router.get("/prediction/accuracy")
def get_accuracy():
    """Get prediction accuracy stats"""
    return get_prediction_accuracy()


@router.post("/prediction/validate")
def trigger_validation():
    """Trigger validation of past predictions"""
    try:
        current = fetch_current_price()
        validate_predictions(current["current_price"])
        return {"message": "Validation complete", "accuracy": get_prediction_accuracy()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Model endpoints
@router.get("/model/metrics")
def get_model_metrics():
    """Get model metrics"""
    from app.predictor import model_loader
    
    if not model_loader.is_loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    return {
        "best_model": model_loader.best_model_name,
        "version": model_loader.metadata.get("version"),
        "created_at": model_loader.metadata.get("created_at"),
        "models_loaded": list(model_loader.models.keys())
    }


@router.get("/model/explainability")
def get_explainability():
    """Get model explainability data"""
    try:
        history = fetch_price_history(hours=6)
        features = engineer_features(history)
        return get_model_explanation_summary(features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/shap")
def get_shap(model_name: Optional[str] = None):
    """Get SHAP values"""
    try:
        history = fetch_price_history(hours=6)
        features = engineer_features(history)
        shap_data = get_shap_values(features, model_name)
        
        if shap_data is None:
            raise HTTPException(status_code=503, detail="SHAP calculation failed")
        
        return shap_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model/importance")
def get_importance(model_name: Optional[str] = None):
    """Get feature importance"""
    importance = get_feature_importance(model_name)
    if importance is None:
        raise HTTPException(status_code=503, detail="Feature importance unavailable")
    return importance


# Market Analysis endpoints
@router.get("/analysis/trend")
def get_trend():
    """Get market trend analysis"""
    try:
        history = fetch_price_history(hours=24)
        features = engineer_features(history)
        return identify_trend(features['price'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/eda")
def get_eda():
    """Get EDA report"""
    try:
        history = fetch_price_history(hours=24)
        features = engineer_features(history)
        return generate_eda_report(features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Drift endpoints
@router.get("/drift/reports")
def get_drift(limit: int = Query(10, ge=1, le=50)):
    """Get drift reports"""
    return get_drift_reports(limit)


@router.get("/drift/summary")
def get_drift_stats():
    """Get drift summary"""
    return get_drift_summary()


# Alert endpoints
@router.get("/alerts")
def get_alerts(limit: int = Query(20, ge=1, le=100)):
    """Get recent alerts"""
    return get_alert_history(limit)


@router.get("/alerts/summary")
def get_alerts_stats():
    """Get alert summary"""
    return get_alert_summary()


# Pipeline endpoints
@router.post("/pipeline/feature")
def run_feature_pipeline():
    """Run feature pipeline"""
    try:
        from pipelines.feature_pipeline import feature_pipeline
        result = feature_pipeline()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/training")
def run_training_pipeline():
    """Run training pipeline"""
    try:
        from pipelines.training_pipeline import training_pipeline
        result = training_pipeline()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pipeline/inference")
def run_inference_pipeline():
    """Run inference pipeline"""
    try:
        from pipelines.inference_pipeline import inference_pipeline
        result = inference_pipeline()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pipeline/status")
def get_pipeline_status():
    """Get pipeline status"""
    from app.predictor import model_loader
    
    return {
        "models_loaded": model_loader.is_loaded,
        "best_model": model_loader.best_model_name if model_loader.is_loaded else None,
        "prediction_history_count": len(get_prediction_history()),
        "drift_reports_count": len(get_drift_reports()),
        "alerts_count": len(get_alert_history()),
        "timestamp": datetime.now().isoformat()
    }

