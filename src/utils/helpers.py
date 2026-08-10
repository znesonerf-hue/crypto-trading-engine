"""Technical Analysis Helpers"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def calculate_rsi(data: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        data: Price series (typically closing prices)
        period: RSI period (default: 14)
    
    Returns:
        RSI series (0-100)
    """
    if len(data) < period + 1:
        return pd.Series(50, index=data.index)  # Return neutral value
    
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_macd(data: pd.Series, fast: int = 12, slow: int = 26, 
                   signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        data: Price series (typically closing prices)
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
    
    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    if len(data) < slow:
        return pd.Series(0, index=data.index), pd.Series(0, index=data.index), pd.Series(0, index=data.index)
    
    # Calculate exponential moving averages
    ema_fast = data.ewm(span=fast, adjust=False).mean()
    ema_slow = data.ewm(span=slow, adjust=False).mean()
    
    # MACD line
    macd_line = ema_fast - ema_slow
    
    # Signal line
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    
    # Histogram
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(data: pd.Series, period: int = 20, 
                             std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands.
    
    Args:
        data: Price series (typically closing prices)
        period: SMA period (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
    
    Returns:
        Tuple of (Upper band, Middle band, Lower band)
    """
    if len(data) < period:
        return pd.Series(0, index=data.index), pd.Series(0, index=data.index), pd.Series(0, index=data.index)
    
    # Middle band (SMA)
    middle_band = data.rolling(window=period).mean()
    
    # Standard deviation
    std = data.rolling(window=period).std()
    
    # Upper and lower bands
    upper_band = middle_band + (std * std_dev)
    lower_band = middle_band - (std * std_dev)
    
    return upper_band, middle_band, lower_band


def calculate_atr(high: pd.Series, low: pd.Series, close: pd.Series, 
                  period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    Args:
        high: High prices
        low: Low prices
        close: Closing prices
        period: ATR period (default: 14)
    
    Returns:
        ATR series
    """
    if len(high) < period:
        return pd.Series(0, index=high.index)
    
    # Calculate True Range
    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    # Calculate ATR
    atr = tr.rolling(window=period).mean()
    
    return atr


def calculate_moving_average(data: pd.Series, period: int = 20, 
                            ma_type: str = "sma") -> pd.Series:
    """
    Calculate Moving Average (SMA or EMA).
    
    Args:
        data: Price series
        period: MA period
        ma_type: Type of MA ('sma' or 'ema')
    
    Returns:
        Moving Average series
    """
    if len(data) < period:
        return pd.Series(data.iloc[0], index=data.index)
    
    if ma_type.lower() == "ema":
        return data.ewm(span=period, adjust=False).mean()
    else:  # SMA
        return data.rolling(window=period).mean()


def calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series,
                        k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate Stochastic Oscillator.
    
    Args:
        high: High prices
        low: Low prices
        close: Closing prices
        k_period: K period (default: 14)
        d_period: D period (default: 3)
    
    Returns:
        Tuple of (%K line, %D line)
    """
    if len(close) < k_period:
        return pd.Series(50, index=close.index), pd.Series(50, index=close.index)
    
    # Lowest low and highest high
    lowest_low = low.rolling(window=k_period).min()
    highest_high = high.rolling(window=k_period).max()
    
    # %K line
    k_line = 100 * (close - lowest_low) / (highest_high - lowest_low)
    
    # %D line (3-period SMA of %K)
    d_line = k_line.rolling(window=d_period).mean()
    
    return k_line, d_line


def calculate_adx(high: pd.Series, low: pd.Series, close: pd.Series,
                  period: int = 14) -> pd.Series:
    """
    Calculate Average Directional Index (ADX).
    
    Args:
        high: High prices
        low: Low prices
        close: Closing prices
        period: ADX period (default: 14)
    
    Returns:
        ADX series (0-100)
    """
    if len(close) < period:
        return pd.Series(0, index=close.index)
    
    # Calculate directional movements
    plus_dm = high.diff()
    minus_dm = low.diff()
    
    plus_dm = plus_dm.where(plus_dm > 0, 0)
    minus_dm = minus_dm.where(minus_dm > 0, 0)
    
    # Calculate true range
    tr = calculate_atr(high, low, close, period=1)
    
    # Calculate directional indicators
    plus_di = 100 * plus_dm / tr
    minus_di = 100 * minus_dm / tr
    
    # Calculate DX
    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
    
    # Calculate ADX (14-period average of DX)
    adx = dx.rolling(window=period).mean()
    
    return adx


def calculate_volume_weighted_average_price(high: pd.Series, low: pd.Series, 
                                            close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Calculate Volume Weighted Average Price (VWAP).
    
    Args:
        high: High prices
        low: Low prices
        close: Closing prices
        volume: Volume
    
    Returns:
        VWAP series
    """
    if len(close) == 0:
        return pd.Series()
    
    # Typical price
    tp = (high + low + close) / 3
    
    # VWAP
    vwap = (tp * volume).cumsum() / volume.cumsum()
    
    return vwap


def calculate_obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """
    Calculate On Balance Volume (OBV).
    
    Args:
        close: Closing prices
        volume: Volume
    
    Returns:
        OBV series
    """
    if len(close) == 0:
        return pd.Series()
    
    obv = volume.copy()
    for i in range(1, len(close)):
        if close.iloc[i] > close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] + volume.iloc[i]
        elif close.iloc[i] < close.iloc[i-1]:
            obv.iloc[i] = obv.iloc[i-1] - volume.iloc[i]
        else:
            obv.iloc[i] = obv.iloc[i-1]
    
    return obv


def calculate_roc(data: pd.Series, period: int = 12) -> pd.Series:
    """
    Calculate Rate of Change (ROC).
    
    Args:
        data: Price series
        period: ROC period (default: 12)
    
    Returns:
        ROC series (as percentage)
    """
    if len(data) < period + 1:
        return pd.Series(0, index=data.index)
    
    roc = ((data - data.shift(period)) / data.shift(period)) * 100
    
    return roc


def calculate_cci(high: pd.Series, low: pd.Series, close: pd.Series,
                  period: int = 20) -> pd.Series:
    """
    Calculate Commodity Channel Index (CCI).
    
    Args:
        high: High prices
        low: Low prices
        close: Closing prices
        period: CCI period (default: 20)
    
    Returns:
        CCI series
    """
    if len(close) < period:
        return pd.Series(0, index=close.index)
    
    # Typical price
    tp = (high + low + close) / 3
    
    # SMA of typical price
    sma_tp = tp.rolling(window=period).mean()
    
    # Mean deviation
    mad = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
    
    # CCI
    cci = (tp - sma_tp) / (0.015 * mad)
    
    return cci


# Formatting Functions

def format_price(price: float, decimals: int = 2) -> str:
    """
    Format price as string.
    
    Args:
        price: Price value
        decimals: Number of decimal places
    
    Returns:
        Formatted price string
    """
    return f"${price:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format percentage as string.
    
    Args:
        value: Percentage value
        decimals: Number of decimal places
    
    Returns:
        Formatted percentage string
    """
    color = "🟢" if value >= 0 else "🔴"
    return f"{color} {value:+.{decimals}f}%"


def round_to_precision(value: float, precision: int = 8) -> float:
    """
    Round value to specific precision.
    
    Args:
        value: Value to round
        precision: Decimal places
    
    Returns:
        Rounded value
    """
    return round(value, precision)


# Utility Functions

def calculate_position_size(portfolio_value: float, risk_percent: float,
                          entry_price: float, stop_loss_price: float) -> float:
    """
    Calculate position size based on risk.
    
    Args:
        portfolio_value: Total portfolio value
        risk_percent: Risk percentage per trade (e.g., 1.0 for 1%)
        entry_price: Entry price
        stop_loss_price: Stop loss price
    
    Returns:
        Position size (quantity)
    """
    if entry_price == stop_loss_price or entry_price == 0:
        return 0
    
    risk_amount = portfolio_value * (risk_percent / 100)
    price_risk = abs(entry_price - stop_loss_price)
    
    position_size = risk_amount / price_risk
    
    return round_to_precision(position_size)


def calculate_time_until_next_candle(current_minute: int, timeframe: str) -> int:
    """
    Calculate minutes until next candle close.
    
    Args:
        current_minute: Current minute (0-59)
        timeframe: Timeframe string ('1m', '5m', '15m', '1h', '4h', '1d')
    
    Returns:
        Minutes until next candle
    """
    timeframe_minutes = {
        '1m': 1, '5m': 5, '15m': 15, '30m': 30,
        '1h': 60, '4h': 240, '1d': 1440
    }
    
    minutes = timeframe_minutes.get(timeframe, 60)
    next_candle_minute = ((current_minute // minutes) + 1) * minutes
    
    return next_candle_minute - current_minute


def calculate_support_resistance(data: pd.Series, window: int = 20) -> Tuple[float, float]:
    """
    Calculate support and resistance levels.
    
    Args:
        data: Price series
        window: Window for calculation
    
    Returns:
        Tuple of (support, resistance)
    """
    if len(data) < window:
        return data.min(), data.max()
    
    support = data.rolling(window=window).min().iloc[-1]
    resistance = data.rolling(window=window).max().iloc[-1]
    
    return support, resistance


def normalize(data: pd.Series) -> pd.Series:
    """
    Normalize data to 0-1 range.
    
    Args:
        data: Data series
    
    Returns:
        Normalized series
    """
    min_val = data.min()
    max_val = data.max()
    
    if max_val == min_val:
        return pd.Series(0.5, index=data.index)
    
    return (data - min_val) / (max_val - min_val)
