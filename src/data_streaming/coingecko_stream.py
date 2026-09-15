"""Real-time Data Streaming from CoinGecko"""

import asyncio
import time
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import threading

from src.connectors.coingecko_connector import CoinGeckoConnector, CryptoPrice

try:
    from src.utils.logger import setup_logger
except ImportError:
    import logging
    def setup_logger(name):
        return logging.getLogger(name)

logger = setup_logger(__name__)


@dataclass
class StreamedPrice:
    """Real-time streamed price update"""
    symbol: str
    price: float
    volume_24h: float
    price_change_24h: float
    market_cap: float
    timestamp: datetime
    source: str = "CoinGecko"


class CoinGeckoDataStream:
    """Real-time data streaming from CoinGecko"""
    
    def __init__(self, update_interval: int = 30):
        """
        Initialize data stream.
        
        Args:
            update_interval: Update interval in seconds (minimum 30 for free API)
        """
        self.connector = CoinGeckoConnector()
        self.update_interval = max(30, update_interval)  # Minimum 30s for free API
        self.subscribers: Dict[str, List[Callable]] = {}  # crypto_id -> callbacks
        self.streaming = False
        self.stream_thread: Optional[threading.Thread] = None
        self.current_prices: Dict[str, StreamedPrice] = {}
        self.price_history: Dict[str, List[StreamedPrice]] = {}
        self.max_history = 1000
    
    def subscribe(self, crypto_id: str, callback: Callable) -> None:
        """
        Subscribe to price updates for a cryptocurrency.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
            callback: Callback function(price: StreamedPrice)
        """
        if crypto_id not in self.subscribers:
            self.subscribers[crypto_id] = []
        self.subscribers[crypto_id].append(callback)
        logger.info(f"Subscribed to {crypto_id}")
    
    def unsubscribe(self, crypto_id: str, callback: Callable) -> None:
        """
        Unsubscribe from price updates.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
            callback: Callback function to remove
        """
        if crypto_id in self.subscribers:
            try:
                self.subscribers[crypto_id].remove(callback)
                logger.info(f"Unsubscribed from {crypto_id}")
            except ValueError:
                pass
    
    def _notify_subscribers(self, crypto_id: str, price: StreamedPrice) -> None:
        """
        Notify all subscribers of price update.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
            price: Streamed price data
        """
        if crypto_id not in self.subscribers:
            return
        
        for callback in self.subscribers[crypto_id]:
            try:
                callback(price)
            except Exception as e:
                logger.error(f"Error in callback for {crypto_id}: {e}")
    
    def _stream_prices(self) -> None:
        """
        Internal method to continuously stream prices.
        """
        logger.info(f"Starting price stream with {self.update_interval}s interval")
        
        while self.streaming:
            try:
                # Get unique crypto IDs from subscribers
                crypto_ids = list(self.subscribers.keys())
                
                if not crypto_ids:
                    time.sleep(self.update_interval)
                    continue
                
                # Fetch prices for all subscribed cryptos
                prices = self.connector.get_multiple_prices(crypto_ids)
                
                for crypto_id, price_data in prices.items():
                    streamed_price = StreamedPrice(
                        symbol=price_data.symbol,
                        price=price_data.price,
                        volume_24h=price_data.volume_24h,
                        price_change_24h=price_data.price_change_24h,
                        market_cap=price_data.market_cap,
                        timestamp=datetime.now()
                    )
                    
                    # Store current price
                    self.current_prices[crypto_id] = streamed_price
                    
                    # Store in history
                    if crypto_id not in self.price_history:
                        self.price_history[crypto_id] = []
                    
                    self.price_history[crypto_id].append(streamed_price)
                    
                    # Keep history size manageable
                    if len(self.price_history[crypto_id]) > self.max_history:
                        self.price_history[crypto_id].pop(0)
                    
                    # Notify subscribers
                    self._notify_subscribers(crypto_id, streamed_price)
                
                time.sleep(self.update_interval)
            
            except Exception as e:
                logger.error(f"Error in price stream: {e}")
                time.sleep(self.update_interval)
    
    def start(self) -> None:
        """
        Start the data stream.
        """
        if self.streaming:
            logger.warning("Stream already running")
            return
        
        self.streaming = True
        self.stream_thread = threading.Thread(target=self._stream_prices, daemon=True)
        self.stream_thread.start()
        logger.info("Data stream started")
    
    def stop(self) -> None:
        """
        Stop the data stream.
        """
        if not self.streaming:
            logger.warning("Stream not running")
            return
        
        self.streaming = False
        if self.stream_thread:
            self.stream_thread.join(timeout=5)
        
        logger.info("Data stream stopped")
    
    def get_current_price(self, crypto_id: str) -> Optional[StreamedPrice]:
        """
        Get most recent streamed price.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
        
        Returns:
            StreamedPrice or None
        """
        return self.current_prices.get(crypto_id)
    
    def get_price_history(self, crypto_id: str, limit: int = 100) -> List[StreamedPrice]:
        """
        Get price history for cryptocurrency.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
            limit: Maximum number of entries
        
        Returns:
            List of StreamedPrice objects
        """
        history = self.price_history.get(crypto_id, [])
        return history[-limit:] if limit else history
    
    def get_statistics(self, crypto_id: str) -> Optional[Dict[str, Any]]:
        """
        Get price statistics from history.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
        
        Returns:
            Statistics dictionary or None
        """
        history = self.price_history.get(crypto_id, [])
        if not history:
            return None
        
        prices = [p.price for p in history]
        volume = [p.volume_24h for p in history]
        
        return {
            'samples': len(history),
            'current_price': prices[-1],
            'min_price': min(prices),
            'max_price': max(prices),
            'avg_price': sum(prices) / len(prices),
            'price_change': prices[-1] - prices[0],
            'price_change_pct': ((prices[-1] - prices[0]) / prices[0] * 100) if prices[0] > 0 else 0,
            'avg_volume': sum(volume) / len(volume) if volume else 0,
            'first_update': history[0].timestamp,
            'last_update': history[-1].timestamp
        }
    
    def is_streaming(self) -> bool:
        """
        Check if stream is active.
        
        Returns:
            True if streaming
        """
        return self.streaming
    
    def get_subscribed_cryptos(self) -> List[str]:
        """
        Get list of subscribed cryptocurrencies.
        
        Returns:
            List of crypto IDs
        """
        return list(self.subscribers.keys())
