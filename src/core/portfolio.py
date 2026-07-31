"""Portfolio Management"""

from datetime import datetime
from typing import Dict, Optional, List
from dataclasses import dataclass, field
import pandas as pd
from src.utils.logger import setup_logger


logger = setup_logger(__name__)


@dataclass
class Balance:
    """Asset balance information"""
    asset: str
    free: float = 0.0
    locked: float = 0.0
    
    @property
    def total(self) -> float:
        return self.free + self.locked


class Portfolio:
    """Portfolio management system"""
    
    def __init__(self, initial_capital: float):
        """
        Initialize portfolio.
        
        Args:
            initial_capital: Initial capital in USDT
        """
        self.initial_capital = initial_capital
        self.balances: Dict[str, Balance] = {
            "USDT": Balance(asset="USDT", free=initial_capital, locked=0.0)
        }
        self.trades: List[Dict] = []
        self.created_at = datetime.now()
    
    def deposit(self, asset: str, amount: float) -> None:
        """
        Add funds to portfolio.
        
        Args:
            asset: Asset symbol
            amount: Amount to deposit
        """
        if asset not in self.balances:
            self.balances[asset] = Balance(asset=asset)
        
        self.balances[asset].free += amount
        logger.info(f"Deposited {amount} {asset}")
    
    def withdraw(self, asset: str, amount: float) -> bool:
        """
        Withdraw funds from portfolio.
        
        Args:
            asset: Asset symbol
            amount: Amount to withdraw
        
        Returns:
            True if successful
        """
        if asset not in self.balances or self.balances[asset].free < amount:
            logger.warning(f"Insufficient balance for withdrawal: {amount} {asset}")
            return False
        
        self.balances[asset].free -= amount
        logger.info(f"Withdrawn {amount} {asset}")
        return True
    
    def lock_balance(self, asset: str, amount: float) -> bool:
        """
        Lock balance for pending orders.
        
        Args:
            asset: Asset symbol
            amount: Amount to lock
        
        Returns:
            True if successful
        """
        if asset not in self.balances or self.balances[asset].free < amount:
            return False
        
        self.balances[asset].free -= amount
        self.balances[asset].locked += amount
        return True
    
    def unlock_balance(self, asset: str, amount: float) -> bool:
        """
        Unlock balance (order cancelled).
        
        Args:
            asset: Asset symbol
            amount: Amount to unlock
        
        Returns:
            True if successful
        """
        if asset not in self.balances or self.balances[asset].locked < amount:
            return False
        
        self.balances[asset].locked -= amount
        self.balances[asset].free += amount
        return True
    
    def get_balance(self, asset: str) -> Balance:
        """
        Get balance for specific asset.
        
        Args:
            asset: Asset symbol
        
        Returns:
            Balance object
        """
        if asset not in self.balances:
            self.balances[asset] = Balance(asset=asset)
        
        return self.balances[asset]
    
    def get_total_balance_usdt(self, prices: Dict[str, float]) -> float:
        """
        Calculate total portfolio value in USDT.
        
        Args:
            prices: Dictionary of {symbol: price}
        
        Returns:
            Total portfolio value in USDT
        """
        total_value = 0.0
        
        for asset, balance in self.balances.items():
            if asset == "USDT":
                total_value += balance.total
            elif asset in prices:
                total_value += balance.total * prices[asset]
            else:
                logger.warning(f"Price not available for {asset}, skipping")
        
        return total_value
    
    def add_trade(self, trade_data: Dict) -> None:
        """
        Record a completed trade.
        
        Args:
            trade_data: Trade information dictionary
        """
        trade_data['timestamp'] = datetime.now()
        self.trades.append(trade_data)
        logger.info(f"Trade recorded: {trade_data['symbol']} {trade_data['side']}")
    
    def get_realized_pnl(self) -> float:
        """
        Calculate total realized PnL from closed trades.
        
        Returns:
            Realized PnL in USDT
        """
        return sum(trade.get('pnl', 0) for trade in self.trades)
    
    def get_win_rate(self) -> float:
        """
        Calculate win rate from trades.
        
        Returns:
            Win rate percentage (0-100)
        """
        if not self.trades:
            return 0.0
        
        winning_trades = sum(1 for trade in self.trades if trade.get('pnl', 0) > 0)
        return (winning_trades / len(self.trades)) * 100
    
    def get_profit_factor(self) -> float:
        """
        Calculate profit factor (gross profit / gross loss).
        
        Returns:
            Profit factor
        """
        winning_sum = sum(max(0, trade.get('pnl', 0)) for trade in self.trades)
        losing_sum = sum(abs(min(0, trade.get('pnl', 0))) for trade in self.trades)
        
        if losing_sum == 0:
            return float('inf') if winning_sum > 0 else 0.0
        
        return winning_sum / losing_sum
    
    def get_trade_stats(self) -> Dict:
        """
        Get comprehensive trade statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "profit_factor": 0.0,
                "avg_trade_duration": 0
            }
        
        winning_trades = [t for t in self.trades if t.get('pnl', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('pnl', 0) <= 0]
        
        total_pnl = sum(t.get('pnl', 0) for t in self.trades)
        avg_duration = sum(t.get('duration', 0) for t in self.trades) / len(self.trades) if self.trades else 0
        
        return {
            "total_trades": len(self.trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": self.get_win_rate(),
            "total_pnl": total_pnl,
            "avg_pnl_per_trade": total_pnl / len(self.trades) if self.trades else 0,
            "largest_win": max((t.get('pnl', 0) for t in winning_trades), default=0),
            "largest_loss": min((t.get('pnl', 0) for t in losing_trades), default=0),
            "profit_factor": self.get_profit_factor(),
            "avg_trade_duration_minutes": avg_duration
        }
    
    def get_summary(self, current_prices: Dict[str, float]) -> Dict:
        """
        Get portfolio summary.
        
        Args:
            current_prices: Current asset prices {symbol: price}
        
        Returns:
            Portfolio summary dictionary
        """
        total_value = self.get_total_balance_usdt(current_prices)
        return_percent = ((total_value - self.initial_capital) / self.initial_capital) * 100
        
        return {
            "initial_capital": self.initial_capital,
            "current_value": total_value,
            "total_return": total_value - self.initial_capital,
            "return_percent": return_percent,
            "realized_pnl": self.get_realized_pnl(),
            "balances": {
                asset: {
                    "free": balance.free,
                    "locked": balance.locked,
                    "total": balance.total
                }
                for asset, balance in self.balances.items()
            },
            "trade_stats": self.get_trade_stats(),
            "created_at": self.created_at
        }
