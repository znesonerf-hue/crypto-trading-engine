"""High-Performance Data Streamer"""

import asyncio
from typing import Callable, Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import deque
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class DataStreamEvent:
    """Data stream event"""
    symbol: str
    data: Dict[str, Any]
    timestamp: datetime


class DataStreamer:
    """High-performance data streaming engine"""
    
    def __init__(self, buffer_size: int = 10000):
        """
        Initialize data streamer.
        
        Args:
            buffer_size: Size of data buffer
        """
        self.buffer = deque(maxlen=buffer_size)
        self.subscribers: Dict[str, List[Callable]] = {}
        self.filters: Dict[str, Callable] = {}
        self.running = False
    
    def subscribe(self, channel: str, callback: Callable) -> None:
        """
        Subscribe to data channel.
        
        Args:
            channel: Channel name
            callback: Callback function
        """
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        
        self.subscribers[channel].append(callback)
        logger.info(f"Subscribed to channel: {channel}")
    
    def unsubscribe(self, channel: str, callback: Callable) -> None:
        """
        Unsubscribe from data channel.
        
        Args:
            channel: Channel name
            callback: Callback function
        """
        if channel in self.subscribers:
            self.subscribers[channel].remove(callback)
    
    def set_filter(self, channel: str, filter_func: Callable) -> None:
        """
        Set filter for channel.
        
        Args:
            channel: Channel name
            filter_func: Filter function
        """
        self.filters[channel] = filter_func
    
    async def stream_data(self, channel: str, data: Dict[str, Any]) -> None:
        """
        Stream data to subscribers.
        
        Args:
            channel: Channel name
            data: Data to stream
        """
        # Apply filter
        if channel in self.filters:
            if not self.filters[channel](data):
                return
        
        # Create event
        event = DataStreamEvent(
            symbol=channel,
            data=data,
            timestamp=datetime.now()
        )
        
        # Add to buffer
        self.buffer.append(event)
        
        # Notify subscribers
        if channel in self.subscribers:
            for callback in self.subscribers[channel]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
    
    def get_buffer_data(self, channel: Optional[str] = None) -> List[DataStreamEvent]:
        """
        Get buffered data.
        
        Args:
            channel: Filter by channel
        
        Returns:
            List of buffered events
        """
        if channel:
            return [e for e in self.buffer if e.symbol == channel]
        return list(self.buffer)
    
    def clear_buffer(self) -> None:
        """
        Clear data buffer.
        """
        self.buffer.clear()
        logger.info("Buffer cleared")
