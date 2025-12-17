"""Feature Engineering - Technical Indicators"""
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from app.config import settings


def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    """Calculate Relative Strength Index"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, 
                   signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate MACD indicator"""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd = ema_fast - ema_slow
    sig = macd.ewm(span=signal, adjust=False).mean()
    return macd, sig, macd - sig


def calculate_bollinger_bands(prices: pd.Series, period: int = 20, 
                              std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """Calculate Bollinger Bands"""
    middle = prices.rolling(window=period).mean()
    std = prices.rolling(window=period).std()
    upper = middle + std * std_dev
    lower = middle - std * std_dev
    return upper, middle, lower


def calculate_moving_averages(prices: pd.Series) -> Dict[str, pd.Series]:
    """Calculate various moving averages"""
    return {
        "sma_5": prices.rolling(5).mean(),
        "sma_10": prices.rolling(10).mean(),
        "sma_20": prices.rolling(20).mean(),
        "ema_5": prices.ewm(span=5, adjust=False).mean(),
        "ema_10": prices.ewm(span=10, adjust=False).mean(),
        "ema_20": prices.ewm(span=20, adjust=False).mean()
    }


def calculate_volatility(prices: pd.Series, period: int = 20) -> pd.Series:
    """Calculate annualized volatility"""
    return prices.pct_change().rolling(window=period).std() * np.sqrt(252)


def calculate_momentum(prices: pd.Series, period: int = 10) -> pd.Series:
    """Calculate price momentum"""
    return prices.diff(period)


def calculate_rate_of_change(prices: pd.Series, period: int = 10) -> pd.Series:
    """Calculate rate of change (ROC)"""
    return ((prices - prices.shift(period)) / prices.shift(period)) * 100


def engineer_features(price_history: List[Dict[str, Any]]) -> pd.DataFrame:
    """Engineer all features from price history"""
    df = pd.DataFrame(price_history)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df = df.set_index('timestamp')
    prices = df['price']
    
    # Basic returns
    df['returns'] = prices.pct_change()
    df['log_returns'] = np.log(prices / prices.shift(1))
    
    # Technical indicators
    df['rsi'] = calculate_rsi(prices, settings.RSI_PERIOD)
    
    macd, signal, hist = calculate_macd(
        prices, settings.MACD_FAST, settings.MACD_SLOW, settings.MACD_SIGNAL
    )
    df['macd'] = macd
    df['macd_signal'] = signal
    df['macd_histogram'] = hist
    
    upper, middle, lower = calculate_bollinger_bands(prices)
    df['bb_upper'] = upper
    df['bb_middle'] = middle
    df['bb_lower'] = lower
    df['bb_width'] = (upper - lower) / middle
    df['bb_position'] = (prices - lower) / (upper - lower)
    
    # Moving averages
    for name, values in calculate_moving_averages(prices).items():
        df[name] = values
    
    df['price_to_sma_20'] = prices / df['sma_20']
    df['sma_5_to_sma_20'] = df['sma_5'] / df['sma_20']
    
    # Volatility & Momentum
    df['volatility'] = calculate_volatility(prices)
    df['momentum_10'] = calculate_momentum(prices, 10)
    df['roc_10'] = calculate_rate_of_change(prices, 10)
    
    # Time features
    df['hour'] = df.index.hour
    df['day_of_week'] = df.index.dayofweek
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
    
    # Lag features
    for lag in [1, 2, 3, 5, 10]:
        df[f'price_lag_{lag}'] = prices.shift(lag)
        df[f'returns_lag_{lag}'] = df['returns'].shift(lag)
    
    # Target variables
    periods = settings.PREDICTION_MINUTES // 5
    df['future_price'] = prices.shift(-periods)
    df['target_direction'] = (df['future_price'] > prices).astype(int)
    df['target_return'] = (df['future_price'] - prices) / prices
    
    return df.dropna()


def get_feature_names() -> List[str]:
    """Get list of feature column names"""
    return [
        'returns', 'log_returns', 'rsi', 'macd', 'macd_signal', 'macd_histogram',
        'bb_width', 'bb_position', 'sma_5', 'sma_10', 'sma_20', 
        'ema_5', 'ema_10', 'ema_20', 'price_to_sma_20', 'sma_5_to_sma_20',
        'volatility', 'momentum_10', 'roc_10', 'hour', 'day_of_week', 'is_weekend',
        'price_lag_1', 'price_lag_2', 'price_lag_3', 'price_lag_5', 'price_lag_10',
        'returns_lag_1', 'returns_lag_2', 'returns_lag_3', 'returns_lag_5', 'returns_lag_10'
    ]

