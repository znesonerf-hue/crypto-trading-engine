"""Risk Management System"""

from datetime import datetime, timedelta
from typing import Optional, Dict, List
from dataclasses import dataclass, field
import pandas as pd
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


@dataclass
class RiskLimits:
    """Risk management limits configuration"""
    max_position_size: float = 0.1  # 10% of portfolio
    stop_loss_percent: float = 2.0  # 2% stop loss
    max_drawdown_percent: float = 10.0  # 10% max drawdown
    daily_loss_limit: float = 1000.0  # Daily loss limit in USDT
    max_open_positions: int = 5  # Maximum concurrent positions
    max_leverage: float = 1.0  # Maximum leverage (1.0 = no leverage)


@dataclass
class Position:
    """Trade position tracking"""
    symbol: str
    entry_price: float
    quantity: float
    entry_time: datetime
    stop_loss: float
    take_profit: Optional[float] = None
    side: str = "BUY"  # BUY or SELL
    unrealized_pnl: float = 0.0
    unrealized_pnl_percent: float = 0.0


class RiskManager:
    """Comprehensive risk management system"""
    
    def __init__(self, limits: RiskLimits):
        """
        Initialize risk manager.
        
        Args:
            limits: Risk limit configuration
        """
        self.limits = limits
        self.positions: Dict[str, Position] = {}
        self.daily_loss = 0.0
        self.daily_loss_reset = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        self.max_drawdown_value = 0.0
        self.peak_balance = 0.0
    
    def check_position_size(self, portfolio_value: float, entry_price: float, 
                           quantity: float, symbol: str) -> bool:
        """
        Check if position size complies with risk limits.
        
        Args:
            portfolio_value: Total portfolio value
            entry_price: Entry price
            quantity: Position quantity
            symbol: Trading symbol
        
        Returns:
            True if position size is acceptable
        """
        position_value = entry_price * quantity
        position_percent = (position_value / portfolio_value) * 100
        
        if position_percent > (self.limits.max_position_size * 100):
            logger.warning(
                f"Position size {position_percent:.2f}% exceeds limit "
                f"{self.limits.max_position_size * 100:.2f}% for {symbol}"
            )
            return False
        
        logger.info(f"Position size check passed: {position_percent:.2f}%")
        return True
    
    def check_open_positions_limit(self) -> bool:
        """
        Check if number of open positions exceeds limit.
        
        Returns:
            True if within limit
        """
        if len(self.positions) >= self.limits.max_open_positions:
            logger.warning(
                f"Maximum open positions ({self.limits.max_open_positions}) reached"
            )
            return False
        
        return True
    
    def check_daily_loss_limit(self, current_loss: float) -> bool:
        """
        Check if daily loss exceeds limit.
        
        Args:
            current_loss: Current daily loss
        
        Returns:
            True if within limit
        """
        # Reset if new day
        now = datetime.now()
        if now.date() > self.daily_loss_reset.date():
            self.daily_loss = 0.0
            self.daily_loss_reset = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        self.daily_loss += current_loss
        
        if self.daily_loss > self.limits.daily_loss_limit:
            logger.error(
                f"Daily loss limit exceeded: ${self.daily_loss:.2f} > "
                f"${self.limits.daily_loss_limit:.2f}"
            )
            return False
        
        logger.info(f"Daily loss: ${self.daily_loss:.2f}/{self.limits.daily_loss_limit:.2f}")
        return True
    
    def check_drawdown(self, current_balance: float) -> bool:
        """
        Check if drawdown exceeds maximum allowed.
        
        Args:
            current_balance: Current portfolio balance
        
        Returns:
            True if within drawdown limit
        """
        # Update peak balance
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
        
        # Calculate drawdown
        if self.peak_balance > 0:
            drawdown_percent = ((self.peak_balance - current_balance) / self.peak_balance) * 100
        else:
            drawdown_percent = 0.0
        
        self.max_drawdown_value = max(self.max_drawdown_value, drawdown_percent)
        
        if drawdown_percent > self.limits.max_drawdown_percent:
            logger.error(
                f"Maximum drawdown exceeded: {drawdown_percent:.2f}% > "
                f"{self.limits.max_drawdown_percent:.2f}%"
            )
            return False
        
        logger.debug(f"Current drawdown: {drawdown_percent:.2f}%")
        return True
    
    def calculate_stop_loss(self, entry_price: float, side: str = "BUY") -> float:
        """
        Calculate stop loss price based on configured percentage.
        
        Args:
            entry_price: Entry price
            side: BUY or SELL
        
        Returns:
            Stop loss price
        """
        if side == "BUY":
            stop_loss = entry_price * (1 - self.limits.stop_loss_percent / 100)
        else:
            stop_loss = entry_price * (1 + self.limits.stop_loss_percent / 100)
        
        return stop_loss
    
    def calculate_position_size(self, portfolio_value: float, entry_price: float,
                               stop_loss_price: float) -> float:
        """
        Calculate optimal position size using Kelly Criterion principles.
        
        Args:
            portfolio_value: Total portfolio value
            entry_price: Entry price
            stop_loss_price: Stop loss price
        
        Returns:
            Position size in base asset
        """
        risk_amount = portfolio_value * self.limits.max_position_size
        price_distance = abs(entry_price - stop_loss_price)
        
        if price_distance == 0:
            return 0
        
        position_size = risk_amount / price_distance
        return position_size
    
    def add_position(self, symbol: str, entry_price: float, quantity: float,
                    stop_loss: float, take_profit: Optional[float] = None,
                    side: str = "BUY") -> Position:
        """
        Add a new position to tracking.
        
        Args:
            symbol: Trading symbol
            entry_price: Entry price
            quantity: Position quantity
            stop_loss: Stop loss price
            take_profit: Take profit price (optional)
            side: BUY or SELL
        
        Returns:
            Position object
        """
        position = Position(
            symbol=symbol,
            entry_price=entry_price,
            quantity=quantity,
            entry_time=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit,
            side=side
        )
        self.positions[symbol] = position
        logger.info(f"Position added: {symbol} {side} {quantity} @ {entry_price}")
        return position
    
    def update_position(self, symbol: str, current_price: float) -> Optional[Position]:
        """
        Update position PnL values.
        
        Args:
            symbol: Trading symbol
            current_price: Current price
        
        Returns:
            Updated position or None
        """
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        if position.side == "BUY":
            position.unrealized_pnl = (current_price - position.entry_price) * position.quantity
            position.unrealized_pnl_percent = ((current_price - position.entry_price) / position.entry_price) * 100
        else:
            position.unrealized_pnl = (position.entry_price - current_price) * position.quantity
            position.unrealized_pnl_percent = ((position.entry_price - current_price) / position.entry_price) * 100
        
        return position
    
    def check_stop_loss(self, symbol: str, current_price: float) -> bool:
        """
        Check if position has hit stop loss.
        
        Args:
            symbol: Trading symbol
            current_price: Current price
        
        Returns:
            True if stop loss is triggered
        """
        if symbol not in self.positions:
            return False
        
        position = self.positions[symbol]
        
        if position.side == "BUY":
            if current_price <= position.stop_loss:
                logger.warning(f"Stop loss triggered for {symbol} at {current_price}")
                return True
        else:
            if current_price >= position.stop_loss:
                logger.warning(f"Stop loss triggered for {symbol} at {current_price}")
                return True
        
        return False
    
    def check_take_profit(self, symbol: str, current_price: float) -> bool:
        """
        Check if position has hit take profit.
        
        Args:
            symbol: Trading symbol
            current_price: Current price
        
        Returns:
            True if take profit is triggered
        """
        if symbol not in self.positions or not self.positions[symbol].take_profit:
            return False
        
        position = self.positions[symbol]
        
        if position.side == "BUY":
            if current_price >= position.take_profit:
                logger.info(f"Take profit triggered for {symbol} at {current_price}")
                return True
        else:
            if current_price <= position.take_profit:
                logger.info(f"Take profit triggered for {symbol} at {current_price}")
                return True
        
        return False
    
    def close_position(self, symbol: str, exit_price: float) -> Optional[Dict]:
        """
        Close a position and return trade summary.
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
        
        Returns:
            Trade summary dictionary
        """
        if symbol not in self.positions:
            return None
        
        position = self.positions[symbol]
        
        if position.side == "BUY":
            pnl = (exit_price - position.entry_price) * position.quantity
        else:
            pnl = (position.entry_price - exit_price) * position.quantity
        
        pnl_percent = (pnl / (position.entry_price * position.quantity)) * 100
        
        trade_summary = {
            "symbol": symbol,
            "side": position.side,
            "entry_price": position.entry_price,
            "exit_price": exit_price,
            "quantity": position.quantity,
            "pnl": pnl,
            "pnl_percent": pnl_percent,
            "duration": (datetime.now() - position.entry_time).total_seconds() / 60,  # minutes
            "entry_time": position.entry_time,
            "exit_time": datetime.now()
        }
        
        del self.positions[symbol]
        logger.info(f"Position closed: {symbol} PnL: ${pnl:.2f} ({pnl_percent:.2f}%)")
        
        return trade_summary
    
    def get_portfolio_heat(self) -> float:
        """
        Calculate total portfolio exposure (heat).
        
        Returns:
            Total exposure as percentage
        """
        total_exposure = sum(
            position.unrealized_pnl_percent 
            for position in self.positions.values()
        )
        return total_exposure
    
    def get_risk_report(self) -> Dict:
        """
        Generate comprehensive risk report.
        
        Returns:
            Risk metrics dictionary
        """
        return {
            "open_positions": len(self.positions),
            "max_positions_allowed": self.limits.max_open_positions,
            "daily_loss": self.daily_loss,
            "daily_loss_limit": self.limits.daily_loss_limit,
            "portfolio_heat": self.get_portfolio_heat(),
            "max_drawdown": self.max_drawdown_value,
            "max_drawdown_limit": self.limits.max_drawdown_percent,
            "positions": {
                symbol: {
                    "entry_price": pos.entry_price,
                    "current_pnl": pos.unrealized_pnl,
                    "pnl_percent": pos.unrealized_pnl_percent
                }
                for symbol, pos in self.positions.items()
            }
        }
