"""Main Trading Engine"""

from typing import Dict, List, Optional
from datetime import datetime
import time
import pandas as pd
import requests
import os
from src.core.portfolio import Portfolio
from src.core.risk_manager import RiskManager, RiskLimits
from src.strategies.base import BaseStrategy, Signal
from src.core.exchange import BitkubMarketData
from src.utils.logger import setup_logger
from src.utils.config import config

logger = setup_logger(__name__)


class TradingEngine:
    """Main trading engine orchestrating all components"""
    
    def __init__(self, mode: str = "paper", initial_capital: float = 10000):
        """
        Initialize trading engine.
        
        Args:
            mode: Trading mode ('paper', 'backtest', or 'live')
            initial_capital: Starting capital
        """
        self.mode = mode
        self.initial_capital = initial_capital
        self.portfolio = Portfolio(initial_capital)
        
        # Initialize risk manager
        risk_limits = RiskLimits(
            max_position_size=config.max_position_size,
            stop_loss_percent=config.stop_loss_percent,
            max_drawdown_percent=config.max_drawdown_percent,
            daily_loss_limit=config.daily_loss_limit,
            max_open_positions=config.max_open_positions
        )
        self.risk_manager = RiskManager(risk_limits)
        
        # Initialize exchange connector (if live/paper)
        self.connector = None
        if mode in ["paper", "live"]:
            
                self.connector = BitkubMarketData()
                    
        
        self.strategies: Dict[str, BaseStrategy] = {}
        self.is_running = False
        self.created_at = datetime.now()
        
        logger.info(f"Trading engine initialized (mode={mode})")
    
    def add_strategy(self, strategy: BaseStrategy) -> None:
        """
        Add trading strategy to engine.
        
        Args:
            strategy: BaseStrategy instance
        """
        strategy_id = f"{strategy.symbol}_{strategy.__class__.__name__}"
        self.strategies[strategy_id] = strategy
        logger.info(f"Strategy added: {strategy_id}")
    
    def remove_strategy(self, strategy_id: str) -> bool:
        """
        Remove trading strategy.
        
        Args:
            strategy_id: Strategy identifier
        
        Returns:
            True if removed successfully
        """
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            logger.info(f"Strategy removed: {strategy_id}")
            return True
        return False
    
    def get_market_data(self, symbol: str, timeframe: str, limit: int = 100) -> pd.DataFrame:
        """
        Get market data for symbol.
        
        Args:
            symbol: Trading symbol
            timeframe: Candle timeframe
            limit: Number of candles
        
        Returns:
            OHLCV DataFrame
        """
        if not self.connector:
            logger.warning("No exchange connector available")
            return pd.DataFrame()
        
        return self.connector.get_klines(symbol, timeframe, limit)
    
    def execute_strategy(self, strategy: BaseStrategy) -> Optional[Dict]:
        """
        Execute strategy and process signal.
        
        Args:
            strategy: Strategy to execute
        
        Returns:
            Trade info if executed, None otherwise
        """
        # Get market data
        data = self.get_market_data(strategy.symbol, strategy.timeframe)
        if data.empty:
            logger.warning(f"No market data for {strategy.symbol}")
            return None

    def notify_telegram(step_name, details):
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            message = (
                f"🔄 *Bot Status: {step_name}*\n\n"
                f"📋 *Details:*\n{details}"
            )
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
            try:
                requests.post(url, json=payload, timeout=5)
            except Exception as e:
                print(f"Telegram notification error: {e}") 
            
        # Calculate signal
        signal = strategy.calculate_signal(data)
        
        # Validate signal
        if not strategy.validate_signal(data, signal):
            return None
        
        if signal == Signal.HOLD:
            return None
        
        # Check risk limits
        portfolio_value = self.portfolio.get_total_balance_usdt(
            {strategy.symbol: data['close'].iloc[-1]}
        )
        
        if not self.risk_manager.check_open_positions_limit():
            logger.warning(f"Max positions reached, skipping {strategy.symbol}")
            return None
        
        # Get entry price and stop loss
        entry_price = strategy.get_entry_price(data, signal)
        stop_loss = strategy.get_stop_loss(entry_price, signal)
        take_profit = strategy.get_take_profit(entry_price, signal)
        
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            portfolio_value, entry_price, stop_loss
        )
        
        # Check position size limit
        if not self.risk_manager.check_position_size(portfolio_value, entry_price, 
                                                      position_size, strategy.symbol):
            logger.warning(f"Position size exceeds limit for {strategy.symbol}")
            return None
        
        # Execute trade
        trade_info = self._execute_trade(
            symbol=strategy.symbol,
            side="BUY" if signal == Signal.BUY else "SELL",
            quantity=position_size,
            entry_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit
        )
        
        if trade_info:
            strategy.update_signal(signal, entry_price)
            self.risk_manager.add_position(
                symbol=strategy.symbol,
                entry_price=entry_price,
                quantity=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                side="BUY" if signal == Signal.BUY else "SELL"
            )
        
        return trade_info
    
    def _execute_trade(self, symbol: str, side: str, quantity: float,
                      entry_price: float, stop_loss: float,
                      take_profit: Optional[float] = None) -> Optional[Dict]:
        """
        Execute trade based on mode.
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Position size
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            Trade execution result
        """
        if self.mode == "paper":
            return self._execute_paper_trade(
                symbol, side, quantity, entry_price, stop_loss, take_profit
            )
        elif self.mode == "live":
            return self._execute_live_trade(
                symbol, side, quantity, entry_price, stop_loss, take_profit
            )
        else:
            return None
    
    def _execute_paper_trade(self, symbol: str, side: str, quantity: float,
                            entry_price: float, stop_loss: float,
                            take_profit: Optional[float] = None) -> Dict:
        """
        Execute paper (simulated) trade.
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Position size
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            Trade execution result
        """
        # Apply simulated slippage
        slippage_factor = 1 + (config.slippage_percent / 100)
        if side == "BUY":
            actual_price = entry_price * slippage_factor
        else:
            actual_price = entry_price / slippage_factor
        
        # Calculate cost
        trade_cost = actual_price * quantity
        
        # Update portfolio
        if side == "BUY":
            quote_asset = symbol.replace('USDT', 'USDT').replace('BUSD', 'BUSD')
            self.portfolio.withdraw('USDT', trade_cost)
            base_asset = symbol.replace('USDT', '').replace('BUSD', '')
            self.portfolio.deposit(base_asset, quantity)
        else:
            base_asset = symbol.replace('USDT', '').replace('BUSD', '')
            self.portfolio.withdraw(base_asset, quantity)
            self.portfolio.deposit('USDT', trade_cost)
        
        trade_result = {
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'entry_price': actual_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'timestamp': datetime.now(),
            'mode': 'paper',
            'status': 'filled'
        }
        
        logger.info(f"Paper trade executed: {side} {quantity} {symbol} @ {actual_price}")
        return trade_result
    
    def _execute_live_trade(self, symbol: str, side: str, quantity: float,
                           entry_price: float, stop_loss: float,
                           take_profit: Optional[float] = None) -> Optional[Dict]:
        """
        Execute live trade on exchange.
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Position size
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
        
        Returns:
            Trade execution result or None
        """
        if not self.connector:
            logger.error("No connector available for live trading")
            return None
        
        # Place market order
        order = self.connector.place_market_order(symbol, side, quantity)
        if not order:
            return None
        
        # Place stop loss order
        if stop_loss:
            self.connector.place_limit_order(
                symbol,
                "SELL" if side == "BUY" else "BUY",
                quantity,
                stop_loss
            )
        
        # Place take profit order (if configured)
        if take_profit:
            self.connector.place_limit_order(
                symbol,
                "SELL" if side == "BUY" else "BUY",
                quantity,
                take_profit
            )
        
        logger.info(f"Live trade executed: {side} {quantity} {symbol}")
        return order
    
    def update_positions(self) -> None:
        """
        Update all open positions and check exit conditions.
        """
        for symbol in list(self.risk_manager.positions.keys()):
            # Get current price
            data = self.get_market_data(symbol, "1h", limit=1)
            if data.empty:
                continue
            
            current_price = data['close'].iloc[-1]
            
            # Update position
            self.risk_manager.update_position(symbol, current_price)
            
            # Check stop loss
            if self.risk_manager.check_stop_loss(symbol, current_price):
                self._close_position(symbol, current_price, "stop_loss")
            
            # Check take profit
            elif self.risk_manager.check_take_profit(symbol, current_price):
                self._close_position(symbol, current_price, "take_profit")
    
    def _close_position(self, symbol: str, exit_price: float, reason: str) -> None:
        """
        Close a position.
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
            reason: Close reason (stop_loss, take_profit, etc.)
        """
        trade_summary = self.risk_manager.close_position(symbol, exit_price)
        if trade_summary:
            self.portfolio.add_trade(trade_summary)
            logger.info(f"Position closed ({reason}): {symbol} PnL: ${trade_summary['pnl']:.2f}")
    
    def run(self, interval_seconds: int = 60) -> None:
        """
        Run trading engine.
        
        Args:
            interval_seconds: Seconds between strategy checks
        """
        self.is_running = True
        logger.info(f"Trading engine started (mode={self.mode})")
        
        try:
            while self.is_running:
                # Update positions
                self.update_positions()
                
                # Execute strategies
                for strategy_id, strategy in self.strategies.items():
                    try:
                        self.execute_strategy(strategy)
                    except Exception as e:
                        logger.error(f"Error executing {strategy_id}: {e}")
                
                # Check risk limits
                portfolio_value = self.portfolio.get_total_balance_usdt({})
                if not self.risk_manager.check_drawdown(portfolio_value):
                    logger.error("Maximum drawdown reached, stopping trading")
                    self.is_running = False
                
                # Sleep before next iteration
                time.sleep(interval_seconds)
        
        except KeyboardInterrupt:
            logger.info("Trading engine stopped by user")
        
        finally:
            self.is_running = False
            logger.info("Trading engine shutdown")
    
    def stop(self) -> None:
        """
        Stop trading engine.
        """
        self.is_running = False
        logger.info("Stop signal sent to trading engine")
    
    def get_summary(self) -> Dict:
        """
        Get engine summary and statistics.
        
        Returns:
            Summary dictionary
        """
        portfolio_value = self.portfolio.get_total_balance_usdt({})
        return {
            'mode': self.mode,
            'status': 'running' if self.is_running else 'stopped',
            'started_at': self.created_at,
            'strategies_active': len(self.strategies),
            'portfolio': self.portfolio.get_summary({}),
            'risk': self.risk_manager.get_risk_report(),
            'uptime_minutes': (datetime.now() - self.created_at).total_seconds() / 60
        }
