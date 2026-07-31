"""Grid Trading Strategy"""

import pandas as pd
from typing import Dict, List
from src.strategies.base import BaseStrategy, Signal
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class GridTradingStrategy(BaseStrategy):
    """Grid trading strategy with automated buy/sell levels"""
    
    def __init__(self, symbol: str, timeframe: str, params=None):
        """
        Initialize Grid Trading strategy.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe
            params: Strategy parameters
                - grid_levels: Number of grid levels (default: 5)
                - grid_range_percent: Grid range percentage (default: 5.0)
                - entry_side: 'long', 'short', or 'both' (default: 'both')
        """
        default_params = {
            'grid_levels': 5,
            'grid_range_percent': 5.0,
            'entry_side': 'both',
            'stop_loss_percent': 3.0
        }
        if params:
            default_params.update(params)
        
        super().__init__(symbol, timeframe, default_params)
        self.grid_levels: Dict[float, bool] = {}  # price: executed
        self.base_price = None
    
    def generate_grid(self, current_price: float) -> Dict[float, str]:
        """
        Generate grid levels.
        
        Args:
            current_price: Current price
        
        Returns:
            Dictionary of {price: 'buy'/'sell'}
        """
        grid_range = current_price * (self.params['grid_range_percent'] / 100)
        level_distance = grid_range / self.params['grid_levels']
        
        grid = {}
        
        if self.params['entry_side'] in ['long', 'both']:
            for i in range(1, self.params['grid_levels'] + 1):
                buy_price = current_price - (level_distance * i)
                grid[buy_price] = 'buy'
        
        if self.params['entry_side'] in ['short', 'both']:
            for i in range(1, self.params['grid_levels'] + 1):
                sell_price = current_price + (level_distance * i)
                grid[sell_price] = 'sell'
        
        return grid
    
    def calculate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Calculate grid trading signal.
        
        Args:
            data: OHLCV data
        
        Returns:
            Trading signal
        """
        current_price = data['close'].iloc[-1]
        
        # Initialize base price on first call
        if self.base_price is None:
            self.base_price = current_price
            self.grid_levels = self.generate_grid(current_price)
            return Signal.HOLD
        
        # Check for grid level crosses
        for level_price in sorted(self.grid_levels.keys()):
            if not self.grid_levels[level_price]:
                if level_price <= current_price:
                    if self.grid_levels == 'buy':
                        self.grid_levels[level_price] = True
                        return Signal.BUY
                elif level_price >= current_price:
                    if self.grid_levels == 'sell':
                        self.grid_levels[level_price] = True
                        return Signal.SELL
        
        return Signal.HOLD
    
    def validate_signal(self, data: pd.DataFrame, signal: Signal) -> bool:
        """
        Validate grid trading signal.
        
        Args:
            data: OHLCV data
            signal: Proposed signal
        
        Returns:
            True if signal is valid
        """
        return signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
