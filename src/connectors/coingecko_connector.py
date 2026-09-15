"""CoinGecko API Connector for Cryptocurrency Data"""

import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

try:
    from pycoingecko import CoinGecko
    COINGECKO_AVAILABLE = True
except ImportError:
    COINGECKO_AVAILABLE = False
    CoinGecko = None

try:
    from src.utils.logger import setup_logger
except ImportError:
    import logging
    def setup_logger(name):
        return logging.getLogger(name)

logger = setup_logger(__name__)


@dataclass
class CryptoPrice:
    """Cryptocurrency price data"""
    symbol: str
    name: str
    price: float
    market_cap: float
    market_cap_rank: int
    volume_24h: float
    price_change_24h: float
    price_change_percentage_24h: float
    circulating_supply: float
    total_supply: float
    timestamp: datetime


@dataclass
class MarketData:
    """Market data from CoinGecko"""
    cryptocurrency: str
    prices: List[Tuple[int, float]]  # (timestamp, price)
    market_caps: List[Tuple[int, float]]
    volumes: List[Tuple[int, float]]
    timestamp: datetime


class CoinGeckoConnector:
    """CoinGecko API Connector"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CoinGecko connector.
        
        Args:
            api_key: Optional API key for higher rate limits (CoinGecko Pro)
        """
        if not COINGECKO_AVAILABLE:
            logger.warning("pycoingecko not installed. Install with: pip install pycoingecko")
            self.cg = None
        else:
            self.cg = CoinGecko()
        
        self.api_key = api_key
        self.rate_limit_delay = 0.5  # 500ms between requests
        self.last_request_time = 0
        self.session = self._create_session()
        self.price_cache: Dict[str, Tuple[CryptoPrice, float]] = {}  # (data, timestamp)
        self.cache_duration = 60  # seconds
        self.market_data_cache: Dict[str, Tuple[MarketData, float]] = {}
    
    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry strategy.
        
        Returns:
            Configured requests session
        """
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session
    
    def _apply_rate_limit(self) -> None:
        """
        Apply rate limiting to respect API limits.
        """
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def get_crypto_price(self, crypto_id: str) -> Optional[CryptoPrice]:
        """
        Get current price for cryptocurrency.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID (e.g., 'bitcoin', 'ethereum')
        
        Returns:
            CryptoPrice object or None if error
        """
        # Check cache
        if crypto_id in self.price_cache:
            data, timestamp = self.price_cache[crypto_id]
            if time.time() - timestamp < self.cache_duration:
                return data
        
        if not self.cg:
            logger.error("CoinGecko not available")
            return None
        
        try:
            self._apply_rate_limit()
            
            data = self.cg.get_price(
                ids=crypto_id,
                vs_currencies='usd',
                include_market_cap=True,
                include_market_cap_rank=True,
                include_24hr_vol=True,
                include_24hr_change=True,
                include_circulating_supply=True
            )
            
            if crypto_id not in data:
                logger.error(f"Cryptocurrency {crypto_id} not found")
                return None
            
            crypto_data = data[crypto_id]
            
            # Get full crypto info
            self._apply_rate_limit()
            crypto_info = self.cg.get_coin_by_id(crypto_id)
            
            price_data = CryptoPrice(
                symbol=crypto_info.get('symbol', 'N/A').upper(),
                name=crypto_info.get('name', 'N/A'),
                price=float(crypto_data.get('usd', 0)),
                market_cap=float(crypto_data.get('usd_market_cap', 0)),
                market_cap_rank=int(crypto_info.get('market_cap_rank', 0) or 0),
                volume_24h=float(crypto_data.get('usd_24h_vol', 0)),
                price_change_24h=float(crypto_data.get('usd_24h_change', 0)),
                price_change_percentage_24h=float(crypto_info.get('market_data', {}).get('price_change_percentage_24h', 0)),
                circulating_supply=float(crypto_info.get('market_data', {}).get('circulating_supply', 0) or 0),
                total_supply=float(crypto_info.get('market_data', {}).get('total_supply', 0) or 0),
                timestamp=datetime.now()
            )
            
            # Cache the result
            self.price_cache[crypto_id] = (price_data, time.time())
            
            return price_data
        
        except Exception as e:
            logger.error(f"Error fetching price for {crypto_id}: {e}")
            return None
    
    def get_market_chart_data(self, crypto_id: str, days: int = 7, 
                             vs_currency: str = 'usd') -> Optional[MarketData]:
        """
        Get market chart data for cryptocurrency.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
            days: Number of days of historical data (1, 7, 30, 90, 365)
            vs_currency: Currency to compare against (default: usd)
        
        Returns:
            MarketData object or None if error
        """
        cache_key = f"{crypto_id}_{days}_{vs_currency}"
        
        if cache_key in self.market_data_cache:
            data, timestamp = self.market_data_cache[cache_key]
            if time.time() - timestamp < self.cache_duration:
                return data
        
        if not self.cg:
            logger.error("CoinGecko not available")
            return None
        
        try:
            self._apply_rate_limit()
            
            market_chart = self.cg.get_coin_market_chart_by_id(
                id=crypto_id,
                vs_currency=vs_currency,
                days=days
            )
            
            market_data = MarketData(
                cryptocurrency=crypto_id,
                prices=market_chart['prices'],
                market_caps=market_chart['market_caps'],
                volumes=market_chart['total_volumes'],
                timestamp=datetime.now()
            )
            
            # Cache the result
            self.market_data_cache[cache_key] = (market_data, time.time())
            
            return market_data
        
        except Exception as e:
            logger.error(f"Error fetching market chart for {crypto_id}: {e}")
            return None
    
    def get_multiple_prices(self, crypto_ids: List[str]) -> Dict[str, CryptoPrice]:
        """
        Get prices for multiple cryptocurrencies.
        
        Args:
            crypto_ids: List of CoinGecko cryptocurrency IDs
        
        Returns:
            Dictionary mapping crypto_id to CryptoPrice
        """
        if not self.cg:
            logger.error("CoinGecko not available")
            return {}
        
        results = {}
        for crypto_id in crypto_ids:
            price = self.get_crypto_price(crypto_id)
            if price:
                results[crypto_id] = price
        
        return results
    
    def get_global_market_data(self) -> Optional[Dict[str, Any]]:
        """
        Get global cryptocurrency market data.
        
        Returns:
            Global market data or None if error
        """
        if not self.cg:
            logger.error("CoinGecko not available")
            return None
        
        try:
            self._apply_rate_limit()
            return self.cg.get_global()
        except Exception as e:
            logger.error(f"Error fetching global market data: {e}")
            return None
    
    def search_cryptocurrency(self, query: str) -> Optional[List[Dict]]:
        """
        Search for cryptocurrency by name or symbol.
        
        Args:
            query: Search query
        
        Returns:
            List of matching cryptocurrencies or None
        """
        if not self.cg:
            logger.error("CoinGecko not available")
            return None
        
        try:
            self._apply_rate_limit()
            results = self.cg.search(query)
            return results.get('coins', [])
        except Exception as e:
            logger.error(f"Error searching for {query}: {e}")
            return None
    
    def get_trending_cryptocurrencies(self) -> Optional[List[Dict]]:
        """
        Get trending cryptocurrencies.
        
        Returns:
            List of trending cryptos or None
        """
        if not self.cg:
            logger.error("CoinGecko not available")
            return None
        
        try:
            self._apply_rate_limit()
            trending = self.cg.get_search_trending()
            return trending.get('coins', [])
        except Exception as e:
            logger.error(f"Error fetching trending cryptos: {e}")
            return None
    
    def get_ohlc_data(self, crypto_id: str, days: int = 30) -> Optional[List[List]]:
        """
        Get OHLC (Open, High, Low, Close) data.
        
        Args:
            crypto_id: CoinGecko cryptocurrency ID
            days: Number of days (1, 7, 30)
        
        Returns:
            List of OHLC data or None
        """
        if not self.cg:
            logger.error("CoinGecko not available")
            return None
        
        try:
            self._apply_rate_limit()
            ohlc = self.cg.get_coin_ohlc_by_id(crypto_id, vs_currency='usd', days=days)
            return ohlc
        except Exception as e:
            logger.error(f"Error fetching OHLC data for {crypto_id}: {e}")
            return None
    
    def clear_cache(self) -> None:
        """
        Clear all cached data.
        """
        self.price_cache.clear()
        self.market_data_cache.clear()
        logger.info("Cache cleared")
    
    def set_cache_duration(self, seconds: int) -> None:
        """
        Set cache duration in seconds.
        
        Args:
            seconds: Cache duration
        """
        self.cache_duration = seconds
        logger.info(f"Cache duration set to {seconds} seconds")
