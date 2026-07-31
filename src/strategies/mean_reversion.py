"""Mean Reversion Trading Strategy"""

import pandas as pd
from src.strategies.base import BaseStrategy, Signal
from src.utils.helpers import calculate_bollinger_bands
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion strategy using Bollinger Bands"""
    
    def __init__(self, symbol: str, timeframe: str, params=None):
        """
        Initialize Mean Reversion strategy.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe
            params: Strategy parameters
                - bb_period: Bollinger Bands period (default: 20)
                - bb_std_dev: Standard deviations (default: 2.0)
                - rsi_period: RSI period (default: 14)
        """
        default_params = {
            'bb_period': 20,
            'bb_std_dev': 2.0,
            'rsi_period': 14,
            'stop_loss_percent': 2.5,
            'take_profit_percent': 4.0
        }
        if params:
            default_params.update(params)
        
        super().__init__(symbol, timeframe, default_params)
    
    def calculate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Calculate mean reversion signal.
        
        Args:
            data: OHLCV data
        
        Returns:
            Trading signal
        """
        if len(data) < self.params['bb_period']:
            return Signal.HOLD
        
        # Calculate Bollinger Bands
        upper_band, middle_band, lower_band = calculate_bollinger_bands(
            data['close'],
            self.params['bb_period'],
            self.params['bb_std_dev']
        )
        
        current_price = data['close'].iloc[-1]
        current_upper = upper_band.iloc[-1]
        current_lower = lower_band.iloc[-1]
        current_middle = middle_band.iloc[-1]
        
        # Buy signal: Price touches lower band and starts recovering
        if (current_price <= current_lower and 
            current_price > data['close'].iloc[-2]):
            return Signal.BUY
        
        # Sell signal: Price touches upper band
        elif current_price >= current_upper:
            return Signal.SELL
        
        return Signal.HOLD
    
    def validate_signal(self, data: pd.DataFrame, signal: Signal) -> bool:
        """
        Validate mean reversion signal.
        
        Args:
            data: OHLCV data
            signal: Proposed signal
        
        Returns:
            True if signal is valid
        """
        if len(data) < self.params['bb_period']:
            return False
        
        if signal == Signal.HOLD:
            return True
        
        # Ensure bands are established (not collapsing)
        upper_band, _, lower_band = calculate_bollinger_bands(
            data['close'],
            self.params['bb_period'],
            self.params['bb_std_dev']
        )
        
        band_width = upper_band.iloc[-1] - lower_band.iloc[-1]
        avg_band_width = (upper_band - lower_band).rolling(window=10).mean().iloc[-1]
        
        if band_width < avg_band_width * 0.5:
            logger.warning(f"Bollinger Bands too narrow for {self.symbol}")
            return False
        
        return True
