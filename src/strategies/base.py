"""Base Strategy Interface"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import pandas as pd
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


class Signal(Enum):
    """Trading signals"""
    BUY = 1
    SELL = -1
    HOLD = 0


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies"""
    
    def __init__(self, symbol: str, timeframe: str, params: Optional[Dict] = None):
        """
        Initialize strategy.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
            timeframe: Candle timeframe (e.g., '1h', '4h', '1d')
            params: Strategy parameters dictionary
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.params = params or {}
        self.last_signal = Signal.HOLD
        self.last_signal_time = None
        self.last_signal_price = None
    
    @abstractmethod
    def calculate_signal(self, data: pd.DataFrame) -> Signal:
        """
        Calculate trading signal based on data.
        
        Args:
            data: OHLCV data as DataFrame with columns: open, high, low, close, volume
        
        Returns:
            Trading signal (BUY, SELL, or HOLD)
        """
        pass
    
    @abstractmethod
    def validate_signal(self, data: pd.DataFrame, signal: Signal) -> bool:
        """
        Validate signal with additional checks.
        
        Args:
            data: OHLCV data
            signal: Proposed signal
        
        Returns:
            True if signal is valid
        """
        pass
    
    def get_entry_price(self, data: pd.DataFrame, signal: Signal) -> float:
        """
        Get recommended entry price for signal.
        
        Args:
            data: OHLCV data
            signal: Trading signal
        
        Returns:
            Entry price
        """
        last_row = data.iloc[-1]
        return last_row['close']
    
    def get_stop_loss(self, entry_price: float, signal: Signal) -> float:
        """
        Calculate stop loss price.
        
        Args:
            entry_price: Entry price
            signal: Trading signal
        
        Returns:
            Stop loss price
        """
        stop_loss_percent = self.params.get('stop_loss_percent', 2.0)
        
        if signal == Signal.BUY:
            return entry_price * (1 - stop_loss_percent / 100)
        else:
            return entry_price * (1 + stop_loss_percent / 100)
    
    def get_take_profit(self, entry_price: float, signal: Signal) -> Optional[float]:
        """
        Calculate take profit price.
        
        Args:
            entry_price: Entry price
            signal: Trading signal
        
        Returns:
            Take profit price or None
        """
        if 'take_profit_percent' not in self.params:
            return None
        
        tp_percent = self.params['take_profit_percent']
        
        if signal == Signal.BUY:
            return entry_price * (1 + tp_percent / 100)
        else:
            return entry_price * (1 - tp_percent / 100)
    
    def update_signal(self, signal: Signal, price: float) -> None:
        """
        Update last signal and metadata.
        
        Args:
            signal: New signal
            price: Price at signal time
        """
        self.last_signal = signal
        self.last_signal_time = datetime.now()
        self.last_signal_price = price
    
    def get_info(self) -> Dict:
        """
        Get strategy information.
        
        Returns:
            Strategy info dictionary
        """
        return {
            'name': self.__class__.__name__,
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'parameters': self.params,
            'last_signal': self.last_signal.name,
            'last_signal_time': self.last_signal_time,
            'last_signal_price': self.last_signal_price
        }
