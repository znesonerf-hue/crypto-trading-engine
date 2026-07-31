"""Strategy tests"""

import pytest
import pandas as pd
from datetime import datetime
from src.strategies.momentum import MomentumStrategy
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.dca import DCAStrategy
from src.strategies.base import Signal


def create_sample_data(length=100):
    """
    Create sample OHLCV data for testing.
    """
    dates = pd.date_range(start='2024-01-01', periods=length, freq='1h')
    data = pd.DataFrame({
        'time': dates,
        'open': [100 + i*0.1 for i in range(length)],
        'high': [101 + i*0.1 for i in range(length)],
        'low': [99 + i*0.1 for i in range(length)],
        'close': [100 + i*0.1 for i in range(length)],
        'volume': [1000 + i*10 for i in range(length)]
    })
    return data


class TestMomentumStrategy:
    
    def test_initialization(self):
        strategy = MomentumStrategy('BTCUSDT', '1h')
        assert strategy.symbol == 'BTCUSDT'
        assert strategy.timeframe == '1h'
    
    def test_signal_calculation(self):
        strategy = MomentumStrategy('BTCUSDT', '1h')
        data = create_sample_data()
        
        signal = strategy.calculate_signal(data)
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
    
    def test_signal_validation(self):
        strategy = MomentumStrategy('BTCUSDT', '1h')
        data = create_sample_data()
        
        signal = strategy.calculate_signal(data)
        is_valid = strategy.validate_signal(data, signal)
        assert isinstance(is_valid, bool)


class TestMeanReversionStrategy:
    
    def test_initialization(self):
        strategy = MeanReversionStrategy('ETHUSDT', '4h')
        assert strategy.symbol == 'ETHUSDT'
        assert strategy.timeframe == '4h'
    
    def test_signal_calculation(self):
        strategy = MeanReversionStrategy('ETHUSDT', '4h')
        data = create_sample_data()
        
        signal = strategy.calculate_signal(data)
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]


class TestDCAStrategy:
    
    def test_initialization(self):
        strategy = DCAStrategy('BTCUSDT', '1d')
        assert strategy.symbol == 'BTCUSDT'
        assert strategy.timeframe == '1d'
    
    def test_signal_at_startup(self):
        strategy = DCAStrategy('BTCUSDT', '1d')
        data = create_sample_data()
        
        # First call should always buy
        signal = strategy.calculate_signal(data)
        assert signal == Signal.BUY
