"""Model Explainability - SHAP and Feature Importance"""
import logging
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd
import shap

from app.predictor import model_loader, ensure_models_loaded
from app.feature_engineering import get_feature_names

logger = logging.getLogger(__name__)


def get_shap_values(features: pd.DataFrame, model_name: Optional[str] = None
                   ) -> Optional[Dict[str, Any]]:
    """Calculate SHAP values for model explanation"""
    if not ensure_models_loaded():
        return None
    
    try:
        if model_name is None:
            model_name = model_loader.best_model_name
        
        model = model_loader.models.get(model_name)
        if model is None:
            logger.warning(f"Model {model_name} not found")
            return None
        
        feature_cols = get_feature_names()
        X = features[feature_cols].copy()
        
        if model_loader.scaler:
            X_scaled = model_loader.scaler.transform(X)
        else:
            X_scaled = X.values
        
        # Use TreeExplainer for tree-based models
        if model_name in ["xgboost", "random_forest", "gradient_boosting"]:
            explainer = shap.TreeExplainer(model)
        else:
            explainer = shap.Explainer(model, X_scaled)
        
        shap_values = explainer.shap_values(X_scaled[-1:])
        
        if isinstance(shap_values, list):
            shap_values = shap_values[0]
        
        values = shap_values.flatten()
        
        # Create feature importance from SHAP
        importance = list(zip(feature_cols, values))
        importance.sort(key=lambda x: abs(x[1]), reverse=True)
        
        return {
            "model_name": model_name,
            "feature_names": feature_cols,
            "shap_values": values.tolist(),
            "top_features": [
                {"feature": f, "importance": round(float(v), 4)}
                for f, v in importance[:10]
            ],
            "expected_value": float(explainer.expected_value) 
                if hasattr(explainer, 'expected_value') 
                and not isinstance(explainer.expected_value, np.ndarray)
                else 0
        }
        
    except Exception as e:
        logger.error(f"SHAP calculation error: {e}")
        return None


def get_feature_importance(model_name: Optional[str] = None
                          ) -> Optional[Dict[str, float]]:
    """Get feature importance from model"""
    if not ensure_models_loaded():
        return None
    
    try:
        if model_name is None:
            model_name = model_loader.best_model_name
        
        model = model_loader.models.get(model_name)
        if model is None:
            return None
        
        feature_cols = get_feature_names()
        
        if hasattr(model, "feature_importances_"):
            importances = model.feature_importances_
        elif hasattr(model, "coef_"):
            importances = np.abs(model.coef_)
        else:
            return None
        
        result = {}
        for name, imp in zip(feature_cols, importances):
            result[name] = round(float(imp), 4)
        
        return dict(sorted(result.items(), key=lambda x: x[1], reverse=True))
        
    except Exception as e:
        logger.error(f"Feature importance error: {e}")
        return None


def get_model_explanation_summary(features: pd.DataFrame
                                 ) -> Dict[str, Any]:
    """Get comprehensive model explanation"""
    shap_data = get_shap_values(features)
    importance = get_feature_importance()
    
    if shap_data is None and importance is None:
        return {"error": "Could not generate explanations"}
    
    top_shap = []
    if shap_data:
        top_shap = shap_data.get("top_features", [])[:5]
    
    top_importance = []
    if importance:
        top_importance = [
            {"feature": k, "importance": v}
            for k, v in list(importance.items())[:5]
        ]
    
    return {
        "shap_top_features": top_shap,
        "importance_top_features": top_importance,
        "model_used": model_loader.best_model_name,
        "explanation": _generate_explanation_text(top_shap, top_importance)
    }


def _generate_explanation_text(shap_features: List[Dict], 
                               importance_features: List[Dict]) -> str:
    """Generate human-readable explanation"""
    if not shap_features and not importance_features:
        return "No explanation available."
    
    parts = []
    
    if shap_features:
        top = shap_features[0]
        direction = "increasing" if top["importance"] > 0 else "decreasing"
        parts.append(
            f"The most influential factor is **{top['feature']}**, "
            f"which is {direction} the predicted price."
        )
    
    if importance_features:
        names = [f["feature"] for f in importance_features[:3]]
        parts.append(
            f"Key features: {', '.join(names)}."
        )
    
    return " ".join(parts)

