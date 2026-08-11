"""Performance Metrics & Dashboard"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics"""
    total_return: float
    annual_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    average_win: float
    average_loss: float
    total_trades: int
    timestamp: datetime


class PerformanceDashboard:
    """Real-time performance dashboard"""
    
    def __init__(self):
        """
        Initialize performance dashboard.
        """
        self.metrics_history: List[PerformanceMetrics] = []
        self.alerts: List[Dict] = []
    
    def calculate_metrics(self, returns: np.ndarray, trades: List[Dict]) -> PerformanceMetrics:
        """
        Calculate performance metrics.
        
        Args:
            returns: Array of returns
            trades: List of trades
        
        Returns:
            Performance metrics
        """
        if len(returns) < 2:
            return None
        
        # Basic metrics
        total_return = np.sum(returns)
        annual_return = np.mean(returns) * 252
        volatility = np.std(returns) * np.sqrt(252)
        
        # Sharpe Ratio
        risk_free_rate = 0.02
        sharpe_ratio = (annual_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Sortino Ratio
        downside_returns = returns[returns < 0]
        downside_volatility = np.std(downside_returns) * np.sqrt(252)
        sortino_ratio = (annual_return - risk_free_rate) / downside_volatility if downside_volatility > 0 else 0
        
        # Max Drawdown
        cumulative = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = np.min(drawdown)
        
        # Calmar Ratio
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Trade metrics
        winning_trades = sum(1 for t in trades if t.get('profit', 0) > 0)
        win_rate = winning_trades / len(trades) if trades else 0
        
        total_profit = sum(t.get('profit', 0) for t in trades if t.get('profit', 0) > 0)
        total_loss = abs(sum(t.get('profit', 0) for t in trades if t.get('profit', 0) < 0))
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        avg_win = total_profit / winning_trades if winning_trades > 0 else 0
        avg_loss = total_loss / (len(trades) - winning_trades) if (len(trades) - winning_trades) > 0 else 0
        
        metrics = PerformanceMetrics(
            total_return=total_return,
            annual_return=annual_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            calmar_ratio=calmar_ratio,
            win_rate=win_rate,
            profit_factor=profit_factor,
            average_win=avg_win,
            average_loss=avg_loss,
            total_trades=len(trades),
            timestamp=datetime.now()
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def get_dashboard_summary(self) -> Dict:
        """
        Get dashboard summary.
        
        Returns:
            Dashboard summary
        """
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        
        return {
            'current_metrics': {
                'total_return': f"{latest.total_return:.2%}",
                'annual_return': f"{latest.annual_return:.2%}",
                'sharpe_ratio': f"{latest.sharpe_ratio:.2f}",
                'max_drawdown': f"{latest.max_drawdown:.2%}",
                'win_rate': f"{latest.win_rate:.2%}",
                'profit_factor': f"{latest.profit_factor:.2f}"
            },
            'alerts': self.alerts,
            'timestamp': latest.timestamp
        }
    
    def check_alerts(self, metrics: PerformanceMetrics) -> None:
        """
        Check for alert conditions.
        
        Args:
            metrics: Performance metrics
        """
        alerts = []
        
        if metrics.max_drawdown < -0.20:
            alerts.append({
                'level': 'CRITICAL',
                'message': f"Max drawdown exceeded: {metrics.max_drawdown:.2%}"
            })
        
        if metrics.win_rate < 0.40:
            alerts.append({
                'level': 'WARNING',
                'message': f"Win rate below threshold: {metrics.win_rate:.2%}"
            })
        
        if metrics.sharpe_ratio < 0.5:
            alerts.append({
                'level': 'WARNING',
                'message': f"Sharpe ratio below target: {metrics.sharpe_ratio:.2f}"
            })
        
        self.alerts = alerts
        for alert in alerts:
            logger.warning(f"{alert['level']}: {alert['message']}")
