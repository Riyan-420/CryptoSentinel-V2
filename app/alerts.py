"""Alert System - Price and Prediction Alerts"""
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from collections import deque

from app.config import settings

logger = logging.getLogger(__name__)

# Alert history
alert_history: deque = deque(maxlen=100)


def check_alerts(current_price: float, 
                 previous_price: float,
                 prediction: Optional[Dict[str, Any]] = None,
                 volatility: Optional[float] = None) -> List[Dict[str, Any]]:
    """Check various alert conditions"""
    alerts = []
    
    # Price change alert
    if previous_price and previous_price > 0:
        change_pct = (current_price - previous_price) / previous_price * 100
        
        if abs(change_pct) > 5:
            alert = {
                "type": "price_change",
                "severity": "high" if abs(change_pct) > 10 else "medium",
                "message": f"Significant price change: {change_pct:+.2f}%",
                "current_price": current_price,
                "previous_price": previous_price,
                "change_percent": round(change_pct, 2),
                "timestamp": datetime.now().isoformat()
            }
            alerts.append(alert)
    
    # Volatility alert
    if volatility is not None and volatility > 0.5:
        alert = {
            "type": "high_volatility",
            "severity": "high" if volatility > 0.8 else "medium",
            "message": f"High volatility detected: {volatility:.2%}",
            "volatility": round(volatility, 4),
            "timestamp": datetime.now().isoformat()
        }
        alerts.append(alert)
    
    # Prediction deviation alert
    if prediction:
        predicted = prediction.get("predicted_price", 0)
        if predicted > 0:
            deviation = abs(current_price - predicted) / current_price * 100
            if deviation > 3:
                alert = {
                    "type": "prediction_deviation",
                    "severity": "medium",
                    "message": f"Price deviating from prediction: {deviation:.2f}%",
                    "current_price": current_price,
                    "predicted_price": predicted,
                    "deviation_percent": round(deviation, 2),
                    "timestamp": datetime.now().isoformat()
                }
                alerts.append(alert)
    
    # Store alerts
    for alert in alerts:
        alert_history.append(alert)
        logger.info(f"Alert: {alert['type']} - {alert['message']}")
    
    return alerts


def check_drawdown_alert(current_price: float, 
                         peak_price: float) -> Optional[Dict[str, Any]]:
    """Check for drawdown from peak"""
    if peak_price <= 0:
        return None
    
    drawdown = (peak_price - current_price) / peak_price * 100
    
    if drawdown > 10:
        alert = {
            "type": "drawdown",
            "severity": "high" if drawdown > 20 else "medium",
            "message": f"Drawdown from peak: {drawdown:.2f}%",
            "current_price": current_price,
            "peak_price": peak_price,
            "drawdown_percent": round(drawdown, 2),
            "timestamp": datetime.now().isoformat()
        }
        alert_history.append(alert)
        return alert
    
    return None


def get_alert_history(limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent alerts"""
    return list(alert_history)[-limit:]


def get_alert_summary() -> Dict[str, Any]:
    """Get alert statistics"""
    if not alert_history:
        return {
            "total_alerts": 0,
            "high_severity": 0,
            "by_type": {}
        }
    
    by_type = {}
    high_count = 0
    
    for alert in alert_history:
        t = alert.get("type", "unknown")
        by_type[t] = by_type.get(t, 0) + 1
        if alert.get("severity") == "high":
            high_count += 1
    
    return {
        "total_alerts": len(alert_history),
        "high_severity": high_count,
        "by_type": by_type
    }


def clear_alerts():
    """Clear alert history"""
    alert_history.clear()

