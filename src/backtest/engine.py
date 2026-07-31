"""Backtesting Engine"""

import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from src.core.portfolio import Portfolio
from src.core.risk_manager import RiskManager, RiskLimits
from src.strategies.base import BaseStrategy, Signal
from src.connectors.binance import BinanceConnector
from src.utils.logger import setup_logger
from src.utils.config import config

logger = setup_logger(__name__)


class BacktestEngine:
    """Backtesting engine for strategy validation"""
    
    def __init__(self, initial_capital: float = 10000):
        """
        Initialize backtest engine.
        
        Args:
            initial_capital: Starting capital for backtest
        """
        self.initial_capital = initial_capital
        self.portfolio = Portfolio(initial_capital)
        
        risk_limits = RiskLimits(
            max_position_size=config.max_position_size,
            stop_loss_percent=config.stop_loss_percent,
            max_drawdown_percent=config.max_drawdown_percent,
            daily_loss_limit=config.daily_loss_limit,
            max_open_positions=config.max_open_positions
        )
        self.risk_manager = RiskManager(risk_limits)
        self.connector = BinanceConnector(
            config.binance_api_key or "",
            config.binance_api_secret or "",
            testnet=True
        )
        
        self.backtest_data: Dict[str, pd.DataFrame] = {}
        self.results: Dict[str, Dict] = {}
        logger.info("Backtest engine initialized")
    
    def load_data(self, symbol: str, start_date: str, end_date: str,
                  timeframe: str = "1h") -> pd.DataFrame:
        """
        Load historical data for backtesting.
        
        Args:
            symbol: Trading symbol
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: Candle timeframe
        
        Returns:
            Historical OHLCV data
        """
        logger.info(f"Loading data: {symbol} {start_date} to {end_date}")
        
        # Get data (would normally load from CSV or database)
        # For now, fetching from Binance
        all_data = []
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        
        while current_date < end_datetime:
            data = self.connector.get_klines(symbol, timeframe, limit=1000)
            if not data.empty:
                data['time'] = pd.to_datetime(data['time'])
                all_data.append(data)
            
            if data.empty:
                break
            
            current_date = data['time'].iloc[-1]
            current_date += timedelta(hours=1)
        
        if all_data:
            df = pd.concat(all_data, ignore_index=True)
            df = df[(df['time'] >= start_date) & (df['time'] <= end_date)]
            self.backtest_data[symbol] = df
            logger.info(f"Loaded {len(df)} candles for {symbol}")
            return df
        
        return pd.DataFrame()
    
    def run_strategy(self, symbol: str, strategy: BaseStrategy,
                     start_date: str, end_date: str) -> Dict:
        """
        Run backtest for strategy.
        
        Args:
            symbol: Trading symbol
            strategy: Strategy to backtest
            start_date: Start date
            end_date: End date
        
        Returns:
            Backtest results
        """
        logger.info(f"Running backtest: {strategy.__class__.__name__} on {symbol}")
        
        # Load data
        data = self.load_data(symbol, start_date, end_date)
        if data.empty:
            logger.error(f"No data available for {symbol}")
            return {}
        
        trades = []
        signals = []
        
        # Iterate through historical data
        for i in range(strategy.params.get('slow_ma', 50), len(data)):
            current_data = data.iloc[:i+1]
            
            # Calculate signal
            signal = strategy.calculate_signal(current_data)
            
            if signal == Signal.HOLD:
                continue
            
            if not strategy.validate_signal(current_data, signal):
                continue
            
            # Record signal
            candle = data.iloc[i]
            entry_price = candle['close']
            stop_loss = strategy.get_stop_loss(entry_price, signal)
            take_profit = strategy.get_take_profit(entry_price, signal)
            
            signals.append({
                'time': candle['time'],
                'signal': signal.name,
                'price': entry_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit
            })
            
            # Find exit (simplified - looking for stop loss or take profit)
            exit_price = None
            exit_time = None
            
            for j in range(i+1, len(data)):
                future_candle = data.iloc[j]
                high = future_candle['high']
                low = future_candle['low']
                
                if signal == Signal.BUY:
                    if take_profit and high >= take_profit:
                        exit_price = take_profit
                        exit_time = future_candle['time']
                        break
                    elif low <= stop_loss:
                        exit_price = stop_loss
                        exit_time = future_candle['time']
                        break
                else:
                    if take_profit and low <= take_profit:
                        exit_price = take_profit
                        exit_time = future_candle['time']
                        break
                    elif high >= stop_loss:
                        exit_price = stop_loss
                        exit_time = future_candle['time']
                        break
            
            # Record trade
            if exit_price:
                pnl = (exit_price - entry_price) if signal == Signal.BUY else (entry_price - exit_price)
                pnl_percent = (pnl / entry_price) * 100
                
                trades.append({
                    'entry_time': signals[-1]['time'],
                    'exit_time': exit_time,
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'pnl_percent': pnl_percent,
                    'side': signal.name
                })
        
        # Calculate statistics
        results = self._calculate_statistics(trades, signals)
        self.results[strategy.__class__.__name__] = results
        
        return results
    
    def _calculate_statistics(self, trades: List[Dict], signals: List[Dict]) -> Dict:
        """
        Calculate backtest statistics.
        
        Args:
            trades: List of completed trades
            signals: List of signals generated
        
        Returns:
            Statistics dictionary
        """
        if not trades:
            return {'total_trades': 0, 'error': 'No trades generated'}
        
        total_pnl = sum(t['pnl'] for t in trades)
        winning_trades = [t for t in trades if t['pnl'] > 0]
        losing_trades = [t for t in trades if t['pnl'] <= 0]
        
        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0
        
        avg_win = sum(t['pnl'] for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t['pnl'] for t in losing_trades) / len(losing_trades) if losing_trades else 0
        
        profit_factor = avg_win / abs(avg_loss) if avg_loss != 0 else float('inf') if avg_win > 0 else 0
        
        # Calculate drawdown
        cumulative_pnl = 0
        peak = 0
        max_drawdown = 0
        
        for trade in trades:
            cumulative_pnl += trade['pnl']
            if cumulative_pnl > peak:
                peak = cumulative_pnl
            drawdown = peak - cumulative_pnl
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'total_signals': len(signals),
            'return_percent': (total_pnl / self.initial_capital) * 100,
            'trades': trades
        }
