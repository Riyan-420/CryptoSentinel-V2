"""Data Ingestion - CoinGecko API"""
import requests
from datetime import datetime
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

COINGECKO_URL = "https://api.coingecko.com/api/v3"


def fetch_current_price() -> Dict[str, Any]:
    """Fetch current Bitcoin price from CoinGecko"""
    try:
        resp = requests.get(
            f"{COINGECKO_URL}/simple/price",
            params={
                "ids": "bitcoin",
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            },
            timeout=10
        )
        resp.raise_for_status()
        btc = resp.json().get("bitcoin", {})
        price = btc.get("usd", 0)
        change = btc.get("usd_24h_change", 0)
        return {
            "current_price": round(price, 2),
            "change_24h": round(price * change / 100, 2),
            "change_percent_24h": round(change, 2)
        }
    except Exception as e:
        logger.error(f"Price fetch error: {e}")
        raise


def fetch_price_history(hours: int = 24) -> List[Dict[str, Any]]:
    """Fetch historical price data"""
    try:
        resp = requests.get(
            f"{COINGECKO_URL}/coins/bitcoin/market_chart",
            params={
                "vs_currency": "usd",
                "days": hours / 24
            },
            timeout=10
        )
        resp.raise_for_status()
        prices = resp.json().get("prices", [])
        return [
            {
                "timestamp": int(ts),
                "price": round(p, 2),
                "time": datetime.fromtimestamp(ts / 1000).strftime("%I:%M %p")
            }
            for ts, p in prices
        ]
    except Exception as e:
        logger.error(f"History fetch error: {e}")
        raise


def fetch_ohlcv_data(hours: int = 24) -> List[Dict[str, Any]]:
    """Fetch OHLCV candle data"""
    try:
        resp = requests.get(
            f"{COINGECKO_URL}/coins/bitcoin/ohlc",
            params={
                "vs_currency": "usd",
                "days": max(1, hours // 24)
            },
            timeout=10
        )
        resp.raise_for_status()
        return [
            {
                "timestamp": int(c[0]),
                "open": round(c[1], 2),
                "high": round(c[2], 2),
                "low": round(c[3], 2),
                "close": round(c[4], 2),
                "volume": 0
            }
            for c in resp.json()
        ]
    except Exception as e:
        logger.error(f"OHLCV fetch error: {e}")
        raise


def fetch_market_data() -> Dict[str, Any]:
    """Fetch comprehensive market data"""
    try:
        resp = requests.get(
            f"{COINGECKO_URL}/coins/bitcoin",
            params={
                "localization": "false",
                "tickers": "false",
                "community_data": "false",
                "developer_data": "false"
            },
            timeout=10
        )
        resp.raise_for_status()
        md = resp.json().get("market_data", {})
        return {
            "current_price": md.get("current_price", {}).get("usd", 0),
            "market_cap": md.get("market_cap", {}).get("usd", 0),
            "total_volume": md.get("total_volume", {}).get("usd", 0),
            "high_24h": md.get("high_24h", {}).get("usd", 0),
            "low_24h": md.get("low_24h", {}).get("usd", 0),
            "price_change_24h": md.get("price_change_24h", 0),
            "price_change_percentage_24h": md.get("price_change_percentage_24h", 0)
        }
    except Exception as e:
        logger.error(f"Market data error: {e}")
        raise

