"""High-Density Mempool Flow & Pending Transaction Sniffer"""

import asyncio
import statistics
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from collections import deque
import hashlib

try:
    from src.utils.logger import setup_logger
except ImportError:
    # Fallback logging if module not available
    import logging
    def setup_logger(name):
        return logging.getLogger(name)

logger = setup_logger(__name__)


@dataclass
class PendingTransaction:
    """Pending transaction in mempool"""
    tx_hash: str
    from_address: str
    to_address: str
    value: float
    gas_price: float
    gas_limit: int
    timestamp: datetime
    nonce: int
    data: str
    priority: int = 0


class MempoolSniffer:
    """Monitor and sniff pending transactions in mempool"""
    
    def __init__(self, max_pool_size: int = 50000):
        """
        Initialize mempool sniffer.
        
        Args:
            max_pool_size: Maximum pending transactions to track
        """
        self.mempool: Dict[str, PendingTransaction] = {}
        self.max_pool_size = max_pool_size
        self.transaction_history: deque = deque(maxlen=max_pool_size)
        self.subscribers: List[Callable] = []
        self.gas_price_history: List[float] = []
        self.detected_patterns: List[Dict] = []
    
    async def monitor_mempool(self, get_pending_txs: Callable) -> None:
        """
        Monitor mempool for pending transactions.
        
        Args:
            get_pending_txs: Function to fetch pending transactions
        """
        while True:
            try:
                pending_txs = await get_pending_txs()
                
                if not isinstance(pending_txs, dict):
                    pending_txs = {}
                
                for tx_hash, tx_data in pending_txs.items():
                    if tx_hash not in self.mempool:
                        tx = PendingTransaction(
                            tx_hash=tx_hash,
                            from_address=tx_data.get('from', ''),
                            to_address=tx_data.get('to', ''),
                            value=float(tx_data.get('value', 0)),
                            gas_price=float(tx_data.get('gasPrice', 0)),
                            gas_limit=int(tx_data.get('gas', 0)),
                            timestamp=datetime.now(),
                            nonce=int(tx_data.get('nonce', 0)),
                            data=tx_data.get('input', '')
                        )
                        
                        self.mempool[tx_hash] = tx
                        self.transaction_history.append(tx)
                        self.gas_price_history.append(tx.gas_price)
                        
                        # Notify subscribers
                        await self._notify_subscribers(tx)
                        
                        # Detect patterns
                        await self._detect_patterns(tx)
                
                # Cleanup old transactions
                if len(self.mempool) > self.max_pool_size:
                    self._cleanup_oldest()
                
                await asyncio.sleep(1)  # Monitor every second
                
            except Exception as e:
                logger.error(f"Error monitoring mempool: {e}")
                await asyncio.sleep(5)
    
    async def _notify_subscribers(self, tx: PendingTransaction) -> None:
        """
        Notify all subscribers of new transaction.
        
        Args:
            tx: Pending transaction
        """
        for subscriber in self.subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber):
                    await subscriber(tx)
                else:
                    subscriber(tx)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")
    
    async def _detect_patterns(self, tx: PendingTransaction) -> None:
        """
        Detect patterns in mempool transactions.
        
        Args:
            tx: Pending transaction
        """
        # Detect sandwich attacks
        if self._is_sandwich_opportunity(tx):
            pattern = {
                'type': 'sandwich_attack',
                'tx_hash': tx.tx_hash,
                'timestamp': datetime.now(),
                'profit_potential': self._estimate_sandwich_profit(tx)
            }
            self.detected_patterns.append(pattern)
            logger.warning(f"Sandwich attack opportunity detected: {tx.tx_hash}")
        
        # Detect MEV extraction
        if self._is_mev_opportunity(tx):
            pattern = {
                'type': 'mev_opportunity',
                'tx_hash': tx.tx_hash,
                'timestamp': datetime.now()
            }
            self.detected_patterns.append(pattern)
            logger.warning(f"MEV opportunity detected: {tx.tx_hash}")
    
    def _is_sandwich_opportunity(self, tx: PendingTransaction) -> bool:
        """
        Check if transaction is sandwich opportunity.
        
        Args:
            tx: Pending transaction
        
        Returns:
            True if opportunity detected
        """
        # Check for DEX interactions with high gas price
        if not self.gas_price_history:
            return False
        
        avg_gas = statistics.mean(self.gas_price_history)
        return tx.gas_price > avg_gas * 1.5
    
    def _is_mev_opportunity(self, tx: PendingTransaction) -> bool:
        """
        Check if transaction is MEV opportunity.
        
        Args:
            tx: Pending transaction
        
        Returns:
            True if opportunity detected
        """
        # Check for large value transfers
        return tx.value > 10  # > 10 ETH equivalent
    
    def _estimate_sandwich_profit(self, tx: PendingTransaction) -> float:
        """
        Estimate profit from sandwich attack.
        
        Args:
            tx: Pending transaction
        
        Returns:
            Estimated profit
        """
        return tx.value * 0.01  # Rough estimate of 1% profit
    
    def _cleanup_oldest(self) -> None:
        """
        Cleanup oldest transactions from mempool.
        """
        if self.mempool:
            oldest = min(self.mempool.values(), key=lambda x: x.timestamp)
            del self.mempool[oldest.tx_hash]
            logger.info(f"Removed oldest transaction from mempool: {oldest.tx_hash}")
    
    def subscribe(self, callback: Callable) -> None:
        """
        Subscribe to mempool updates.
        
        Args:
            callback: Callback function
        """
        self.subscribers.append(callback)
    
    def get_gas_price_trend(self) -> Dict:
        """
        Get gas price trend analysis.
        
        Returns:
            Gas price statistics
        """
        if not self.gas_price_history:
            return {}
        
        return {
            'current': self.gas_price_history[-1],
            'average': statistics.mean(self.gas_price_history),
            'median': statistics.median(self.gas_price_history),
            'min': min(self.gas_price_history),
            'max': max(self.gas_price_history),
            'trend': 'up' if self.gas_price_history[-1] > statistics.mean(self.gas_price_history) else 'down'
        }
