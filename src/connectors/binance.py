"""Binance API Connector"""

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from typing import Dict, List, Optional, Tuple
import pandas as pd
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class BinanceConnector:
    """Binance API wrapper for trading operations"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Binance connector.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet if True
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            logger.info(f"Binance connector initialized (testnet={testnet})")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            raise
    
    def get_account_balance(self) -> Dict[str, Dict[str, float]]:
        """
        Get account balance and available funds.
        
        Returns:
            Dictionary of {asset: {free, locked, total}}
        """
        try:
            account = self.client.get_account()
            balances = {}
            
            for balance in account['balances']:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                
                if free > 0 or locked > 0:
                    balances[asset] = {
                        'free': free,
                        'locked': locked,
                        'total': free + locked
                    }
            
            return balances
        except BinanceAPIException as e:
            logger.error(f"API error getting account balance: {e}")
            return {}
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for symbol.
        
        Args:
            symbol: Trading symbol (e.g., 'BTCUSDT')
        
        Returns:
            Current price or None
        """
        try:
            price_data = self.client.get_symbol_info(symbol)
            if price_data:
                ticker = self.client.get_ticker(symbol=symbol)
                return float(ticker['lastPrice'])
        except BinanceAPIException as e:
            logger.error(f"API error getting price for {symbol}: {e}")
        
        return None
    
    def get_klines(self, symbol: str, interval: str, limit: int = 100) -> pd.DataFrame:
        """
        Get historical candlestick data.
        
        Args:
            symbol: Trading symbol
            interval: Time interval (e.g., '1h', '4h', '1d')
            limit: Number of candles to fetch
        
        Returns:
            DataFrame with OHLCV data
        """
        try:
            klines = self.client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            
            df = pd.DataFrame(klines, columns=[
                'time', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            df['time'] = pd.to_datetime(df['time'], unit='ms')
            df['open'] = df['open'].astype(float)
            df['high'] = df['high'].astype(float)
            df['low'] = df['low'].astype(float)
            df['close'] = df['close'].astype(float)
            df['volume'] = df['volume'].astype(float)
            
            return df[['time', 'open', 'high', 'low', 'close', 'volume']]
        
        except BinanceAPIException as e:
            logger.error(f"API error getting klines for {symbol}: {e}")
            return pd.DataFrame()
    
    def place_market_order(self, symbol: str, side: str, quantity: float) -> Optional[Dict]:
        """
        Place market order.
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
        
        Returns:
            Order result or None
        """
        try:
            order = self.client.order_market(
                symbol=symbol,
                side=side,
                quantity=quantity
            )
            
            logger.info(f"Market order placed: {side} {quantity} {symbol}")
            return order
        
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error(f"Error placing market order: {e}")
            return None
    
    def place_limit_order(self, symbol: str, side: str, quantity: float, 
                         price: float) -> Optional[Dict]:
        """
        Place limit order.
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
        
        Returns:
            Order result or None
        """
        try:
            order = self.client.order_limit(
                symbol=symbol,
                side=side,
                quantity=quantity,
                price=price
            )
            
            logger.info(f"Limit order placed: {side} {quantity} {symbol} @ {price}")
            return order
        
        except (BinanceAPIException, BinanceOrderException) as e:
            logger.error(f"Error placing limit order: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Cancel existing order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel
        
        Returns:
            Cancellation result or None
        """
        try:
            result = self.client.cancel_order(symbol=symbol, orderId=order_id)
            logger.info(f"Order cancelled: {order_id}")
            return result
        
        except BinanceAPIException as e:
            logger.error(f"Error cancelling order: {e}")
            return None
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """
        Get open orders.
        
        Args:
            symbol: Optional symbol filter
        
        Returns:
            List of open orders
        """
        try:
            if symbol:
                orders = self.client.get_open_orders(symbol=symbol)
            else:
                orders = self.client.get_open_orders()
            
            return orders
        
        except BinanceAPIException as e:
            logger.error(f"Error getting open orders: {e}")
            return []
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Get order status.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
        
        Returns:
            Order status or None
        """
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return order
        
        except BinanceAPIException as e:
            logger.error(f"Error getting order status: {e}")
            return None
