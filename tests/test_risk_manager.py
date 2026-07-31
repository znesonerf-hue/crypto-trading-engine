"""Risk manager tests"""

import pytest
from src.core.risk_manager import RiskManager, RiskLimits, Position
from datetime import datetime


class TestRiskManager:
    
    @pytest.fixture
    def risk_manager(self):
        limits = RiskLimits(
            max_position_size=0.1,
            stop_loss_percent=2.0,
            max_drawdown_percent=10.0,
            daily_loss_limit=1000.0,
            max_open_positions=5
        )
        return RiskManager(limits)
    
    def test_position_size_check(self, risk_manager):
        portfolio_value = 10000
        entry_price = 100
        quantity = 10
        symbol = 'BTCUSDT'
        
        result = risk_manager.check_position_size(portfolio_value, entry_price, quantity, symbol)
        assert isinstance(result, bool)
    
    def test_max_positions_check(self, risk_manager):
        result = risk_manager.check_open_positions_limit()
        assert result == True
        
        # Add max positions
        for i in range(5):
            risk_manager.add_position(f'SYM{i}', 100, 1, 98)
        
        result = risk_manager.check_open_positions_limit()
        assert result == False
    
    def test_stop_loss_calculation(self, risk_manager):
        entry_price = 100
        stop_loss = risk_manager.calculate_stop_loss(entry_price, side='BUY')
        
        expected = 100 * (1 - 2.0 / 100)
        assert stop_loss == pytest.approx(expected, rel=0.01)
    
    def test_add_position(self, risk_manager):
        position = risk_manager.add_position(
            symbol='BTCUSDT',
            entry_price=100,
            quantity=1,
            stop_loss=98
        )
        
        assert position.symbol == 'BTCUSDT'
        assert position.entry_price == 100
        assert 'BTCUSDT' in risk_manager.positions
    
    def test_check_stop_loss(self, risk_manager):
        risk_manager.add_position('BTCUSDT', 100, 1, 98)
        
        # Price above stop loss
        assert risk_manager.check_stop_loss('BTCUSDT', 99) == False
        
        # Price at stop loss
        assert risk_manager.check_stop_loss('BTCUSDT', 98) == True
