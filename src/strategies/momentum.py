"""Momentum Trading Strategy"""

import pandas as pd
from src.strategies.base import BaseStrategy, Signal
from src.utils.helpers import calculate_macd, calculate_rsi
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy using technical indicators"""
    
    def __init__(self, symbol: str, timeframe: str, params=None):
        """
        Initialize Momentum strategy.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe
            params: Strategy parameters
                - fast_ma: Fast moving average period (default: 20)
                - slow_ma: Slow moving average period (default: 50)
                - rsi_period: RSI period (default: 14)
                - rsi_overbought: RSI overbought threshold (default: 70)
                - rsi_oversold: RSI oversold threshold (default: 30)
                - min_volume_ratio: Minimum volume ratio vs average (default: 1.2)
        """
        default_params = {
            'fast_ma': 20,
            'slow_ma': 50,
            'rsi_period': 14,
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'min_volume_ratio': 1.2,
            'stop_loss_percent': 2.0,
            'take_profit_percent': 5.0
        }
        if params:
            default_params.update(params)
        
        super().__init__(symbol, timeframe, default_params)
    
    def calculate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Calculate momentum signal.
        
        Args:
            data: OHLCV data
        
        Returns:
            Trading signal
        """
        if len(data) < self.params['slow_ma']:
            return Signal.HOLD
        
        # Calculate moving averages
        fast_ma = data['close'].rolling(window=self.params['fast_ma']).mean()
        slow_ma = data['close'].rolling(window=self.params['slow_ma']).mean()
        
        # Calculate RSI
        rsi = calculate_rsi(data['close'], self.params['rsi_period'])
        
        # Get current values
        current_fast = fast_ma.iloc[-1]
        current_slow = slow_ma.iloc[-1]
        current_rsi = rsi.iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].rolling(window=20).mean().iloc[-1]
        
        # Buy signal: Fast MA above Slow MA, RSI oversold, volume surge
        if (current_fast > current_slow and 
            current_rsi < self.params['rsi_overbought'] and
            current_volume > avg_volume * self.params['min_volume_ratio']):
            return Signal.BUY
        
        # Sell signal: Fast MA below Slow MA, RSI overbought
        elif (current_fast < current_slow and
              current_rsi > self.params['rsi_oversold']):
            return Signal.SELL
        
        return Signal.HOLD
    
    def validate_signal(self, data: pd.DataFrame, signal: Signal) -> bool:
        """
        Validate momentum signal.
        
        Args:
            data: OHLCV data
            signal: Proposed signal
        
        Returns:
            True if signal is valid
        """
        if len(data) < self.params['slow_ma']:
            return False
        
        if signal == Signal.HOLD:
            return True
        
        # Ensure sufficient volume
        recent_volume = data['volume'].iloc[-5:].mean()
        if recent_volume < data['volume'].iloc[-1] * 0.5:
            logger.warning(f"Volume check failed for {self.symbol}")
            return False
        
        # Ensure price is moving
        recent_price_range = (data['high'].iloc[-5:].max() - data['low'].iloc[-5:].min()) / data['close'].iloc[-1]
        if recent_price_range < 0.01:  # Less than 1% movement
            logger.warning(f"Insufficient price movement for {self.symbol}")
            return False
        
        return True
