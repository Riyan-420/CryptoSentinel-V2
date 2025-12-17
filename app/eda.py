"""Exploratory Data Analysis - Trends and Anomalies"""
import logging
from typing import Dict, Any, List, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def identify_trend(prices: pd.Series, window: int = 20) -> Dict[str, Any]:
    """Identify price trend using moving averages"""
    if len(prices) < window:
        return {"trend": "insufficient_data", "strength": 0}
    
    sma = prices.rolling(window=window).mean()
    current = prices.iloc[-1]
    ma_current = sma.iloc[-1]
    
    # Calculate slope
    if len(sma.dropna()) > 5:
        recent_ma = sma.dropna().tail(5)
        slope = (recent_ma.iloc[-1] - recent_ma.iloc[0]) / len(recent_ma)
        slope_pct = slope / current * 100
    else:
        slope_pct = 0
    
    # Determine trend
    if current > ma_current * 1.02:
        trend = "bullish"
        strength = min(1.0, (current / ma_current - 1) * 10)
    elif current < ma_current * 0.98:
        trend = "bearish"
        strength = min(1.0, (1 - current / ma_current) * 10)
    else:
        trend = "neutral"
        strength = 0.2
    
    return {
        "trend": trend,
        "strength": round(strength, 2),
        "current_price": round(current, 2),
        "sma_20": round(ma_current, 2),
        "slope_pct": round(slope_pct, 4),
        "description": f"{trend.capitalize()} trend with {strength*100:.0f}% strength"
    }


def detect_anomalies(prices: pd.Series, std_threshold: float = 2.0
                    ) -> List[Dict[str, Any]]:
    """Detect price anomalies using z-score"""
    if len(prices) < 20:
        return []
    
    mean = prices.rolling(window=20).mean()
    std = prices.rolling(window=20).std()
    z_scores = (prices - mean) / std
    
    anomalies = []
    for i, (idx, z) in enumerate(z_scores.items()):
        if abs(z) > std_threshold:
            anomalies.append({
                "timestamp": str(idx),
                "price": round(float(prices.iloc[i]), 2),
                "z_score": round(float(z), 2),
                "type": "spike" if z > 0 else "drop",
                "severity": "high" if abs(z) > 3 else "medium"
            })
    
    return anomalies[-10:]  # Return last 10


def calculate_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate comprehensive statistics"""
    if 'price' not in df.columns:
        return {}
    
    prices = df['price']
    
    stats = {
        "count": len(prices),
        "mean": round(prices.mean(), 2),
        "median": round(prices.median(), 2),
        "std": round(prices.std(), 2),
        "min": round(prices.min(), 2),
        "max": round(prices.max(), 2),
        "range": round(prices.max() - prices.min(), 2),
        "skewness": round(float(prices.skew()), 4),
        "kurtosis": round(float(prices.kurtosis()), 4)
    }
    
    # Returns statistics
    if 'returns' in df.columns:
        returns = df['returns'].dropna()
        stats["returns_mean"] = round(returns.mean() * 100, 4)
        stats["returns_std"] = round(returns.std() * 100, 4)
        stats["sharpe_ratio"] = round(
            returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0, 4
        )
    
    return stats


def calculate_correlation_matrix(df: pd.DataFrame, 
                                 features: List[str] = None
                                ) -> Dict[str, Any]:
    """Calculate correlation matrix for features"""
    if features is None:
        features = ['price', 'rsi', 'macd', 'volatility', 'momentum_10']
    
    available = [f for f in features if f in df.columns]
    if len(available) < 2:
        return {"error": "Insufficient features for correlation"}
    
    corr_matrix = df[available].corr()
    
    return {
        "features": available,
        "matrix": corr_matrix.round(4).to_dict(),
        "top_correlations": _get_top_correlations(corr_matrix)
    }


def _get_top_correlations(corr_matrix: pd.DataFrame, n: int = 5
                         ) -> List[Dict[str, Any]]:
    """Get top N correlations"""
    correlations = []
    
    for i, col1 in enumerate(corr_matrix.columns):
        for j, col2 in enumerate(corr_matrix.columns):
            if i < j:  # Upper triangle only
                correlations.append({
                    "feature_1": col1,
                    "feature_2": col2,
                    "correlation": round(corr_matrix.loc[col1, col2], 4)
                })
    
    correlations.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return correlations[:n]


def generate_eda_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Generate comprehensive EDA report"""
    if 'price' not in df.columns:
        return {"error": "Price column required"}
    
    prices = df['price']
    
    return {
        "trend": identify_trend(prices),
        "statistics": calculate_statistics(df),
        "anomalies": detect_anomalies(prices),
        "correlations": calculate_correlation_matrix(df),
        "data_quality": {
            "total_rows": len(df),
            "missing_values": df.isnull().sum().to_dict(),
            "duplicates": int(df.duplicated().sum())
        }
    }

