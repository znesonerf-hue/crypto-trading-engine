"""Dollar Cost Averaging (DCA) Strategy"""

import pandas as pd
from datetime import datetime, timedelta
from src.strategies.base import BaseStrategy, Signal
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class DCAStrategy(BaseStrategy):
    """Dollar Cost Averaging strategy for systematic accumulation"""
    
    def __init__(self, symbol: str, timeframe: str, params=None):
        """
        Initialize DCA strategy.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe
            params: Strategy parameters
                - dca_amount: Amount to buy per period (default: 100)
                - dca_interval_hours: Hours between purchases (default: 24)
                - max_position_value: Maximum position value (default: 10000)
        """
        default_params = {
            'dca_amount': 100,  # USDT per purchase
            'dca_interval_hours': 24,
            'max_position_value': 10000,
            'stop_loss_percent': 10.0,  # DCA typically has lower stops
        }
        if params:
            default_params.update(params)
        
        super().__init__(symbol, timeframe, default_params)
        self.last_dca_time = None
    
    def calculate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Calculate DCA signal based on time interval.
        
        Args:
            data: OHLCV data
        
        Returns:
            Trading signal
        """
        now = datetime.now()
        
        # Initialize on first call
        if self.last_dca_time is None:
            self.last_dca_time = now
            return Signal.BUY
        
        # Check if enough time has passed
        time_since_last = (now - self.last_dca_time).total_seconds() / 3600  # hours
        
        if time_since_last >= self.params['dca_interval_hours']:
            self.last_dca_time = now
            return Signal.BUY
        
        return Signal.HOLD
    
    def validate_signal(self, data: pd.DataFrame, signal: Signal) -> bool:
        """
        Validate DCA signal.
        
        Args:
            data: OHLCV data
            signal: Proposed signal
        
        Returns:
            True if signal is valid
        """
        if signal != Signal.BUY:
            return True
        
        # Ensure market is open and liquid
        if len(data) < 2:
            return False
        
        # Check for reasonable spread
        last_candle = data.iloc[-1]
        spread = (last_candle['high'] - last_candle['low']) / last_candle['close']
        
        if spread > 0.05:  # More than 5% spread is unusual
            logger.warning(f"High spread detected for {self.symbol}: {spread:.2%}")
            return False
        
        return True
