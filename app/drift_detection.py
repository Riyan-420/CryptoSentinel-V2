"""Data Drift Detection - DeepChecks"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

import pandas as pd

from app.config import settings

logger = logging.getLogger(__name__)

# Global state - single report and reference data
_drift_report: Optional[Dict[str, Any]] = None
_reference_data: Optional[pd.DataFrame] = None


def set_reference_data(df: pd.DataFrame):
    """Set baseline data for drift comparison"""
    global _reference_data
    _reference_data = df.copy()
    logger.info(f"Reference data set: {len(df)} samples")


def detect_drift(current_data: pd.DataFrame, feature_columns: List[str]) -> Dict[str, Any]:
    """
    Detect drift by comparing current data against reference baseline.
    Uses DeepChecks if available, falls back to KS-test.
    """
    global _drift_report, _reference_data
    
    if _reference_data is None:
        return {
            "drift_detected": False,
            "drift_score": 0.0,
            "message": "No reference data set",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Try DeepChecks first
        from deepchecks.tabular import Dataset
        from deepchecks.tabular.checks import DatasetDrift
        
        ref_dataset = Dataset(_reference_data[feature_columns], label=None)
        cur_dataset = Dataset(current_data[feature_columns], label=None)
        
        result = DatasetDrift().run(ref_dataset, cur_dataset)
        score = result.value.get('domain_classifier_drift_score', 0.0)
        
        _drift_report = {
            "drift_detected": score > settings.DRIFT_THRESHOLD,
            "drift_score": float(score),
            "threshold": settings.DRIFT_THRESHOLD,
            "feature_drifts": result.value.get('feature_drifts', {}),
            "method": "deepchecks",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Drift check: score={score:.4f}, detected={_drift_report['drift_detected']}")
        return _drift_report
        
    except ImportError:
        logger.warning("DeepChecks not available, using KS-test fallback")
        return _simple_drift_detection(current_data, feature_columns)
    except Exception as e:
        logger.error(f"Drift detection error: {e}")
        return {
            "drift_detected": False,
            "drift_score": 0.0,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def _simple_drift_detection(current_data: pd.DataFrame, 
                           feature_columns: List[str]) -> Dict[str, Any]:
    """Fallback: KS-test for each feature"""
    global _drift_report, _reference_data
    
    if _reference_data is None:
        return {"drift_detected": False, "drift_score": 0.0}
    
    from scipy import stats
    
    feature_drifts = {}
    total = 0.0
    
    for col in feature_columns:
        if col in _reference_data.columns and col in current_data.columns:
            ref_vals = _reference_data[col].dropna()
            cur_vals = current_data[col].dropna()
            
            if len(ref_vals) > 0 and len(cur_vals) > 0:
                stat, pval = stats.ks_2samp(ref_vals, cur_vals)
                feature_drifts[col] = {
                    "statistic": float(stat),
                    "p_value": float(pval),
                    "drifted": pval < 0.05
                }
                total += stat
    
    avg_score = total / len(feature_columns) if feature_columns else 0
    
    _drift_report = {
        "drift_detected": avg_score > settings.DRIFT_THRESHOLD,
        "drift_score": float(avg_score),
        "threshold": settings.DRIFT_THRESHOLD,
        "feature_drifts": feature_drifts,
        "method": "ks_test",
        "timestamp": datetime.now().isoformat()
    }
    
    logger.info(f"Drift check (KS): score={avg_score:.4f}, detected={_drift_report['drift_detected']}")
    return _drift_report


def get_drift_report() -> Dict[str, Any]:
    """Get the current drift report"""
    return _drift_report or {
        "drift_detected": False,
        "drift_score": 0.0,
        "message": "No analysis yet",
        "timestamp": datetime.now().isoformat()
    }


def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """Check data quality metrics"""
    report = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "missing_values": {},
        "duplicates": int(df.duplicated().sum()),
        "timestamp": datetime.now().isoformat()
    }
    
    for col in df.columns:
        missing = int(df[col].isna().sum())
        if missing > 0:
            report["missing_values"][col] = {
                "count": missing,
                "pct": round(missing / len(df) * 100, 2)
            }
    
    return report
