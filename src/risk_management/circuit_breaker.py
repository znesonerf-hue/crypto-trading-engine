"""Circuit Breaker & Emergency Stop"""

from typing import Callable, Dict, Optional
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Stop trading
    HALF_OPEN = "half_open"  # Test recovery


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    max_drawdown_limit: float = -0.20  # -20%
    daily_loss_limit: float = 1000.0
    daily_loss_check_hour: int = 0  # Check at midnight


class CircuitBreaker:
    """Emergency stop and circuit breaker system"""
    
    def __init__(self, config: CircuitBreakerConfig = None):
        """
        Initialize circuit breaker.
        
        Args:
            config: Circuit breaker configuration
        """
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.last_state_change = datetime.now()
        self.daily_loss = 0.0
        self.last_check_date = datetime.now().date()
    
    def can_trade(self) -> bool:
        """
        Check if trading is allowed.
        
        Returns:
            True if trading is allowed
        """
        return self.state == CircuitState.CLOSED
    
    def record_failure(self) -> None:
        """
        Record a trade failure.
        """
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.config.failure_threshold:
            self.trip()
            logger.error(f"Circuit breaker TRIPPED after {self.failure_count} failures")
    
    def record_success(self) -> None:
        """
        Record a successful trade.
        """
        self.failure_count = max(0, self.failure_count - 1)
        
        if self.state == CircuitState.HALF_OPEN:
            self.reset()
            logger.info("Circuit breaker RESET to CLOSED")
    
    def trip(self) -> None:
        """
        Trip the circuit breaker (open state).
        """
        self.state = CircuitState.OPEN
        self.last_state_change = datetime.now()
        logger.critical("CIRCUIT BREAKER TRIPPED - TRADING HALTED")
    
    def reset(self) -> None:
        """
        Reset the circuit breaker.
        """
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.last_state_change = datetime.now()
        logger.info("Circuit breaker RESET")
    
    def check_recovery(self) -> None:
        """
        Check if circuit breaker can recover.
        """
        if self.state == CircuitState.OPEN:
            time_since_trip = (datetime.now() - self.last_state_change).total_seconds()
            
            if time_since_trip >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker entering HALF_OPEN state")
    
    def check_drawdown(self, current_drawdown: float) -> None:
        """
        Check drawdown limit.
        
        Args:
            current_drawdown: Current drawdown percentage
        """
        if current_drawdown <= self.config.max_drawdown_limit:
            logger.critical(f"Max drawdown exceeded: {current_drawdown:.2%}")
            self.trip()
    
    def check_daily_loss(self, daily_loss: float) -> None:
        """
        Check daily loss limit.
        
        Args:
            daily_loss: Daily loss amount
        """
        # Reset daily loss at specified hour
        if datetime.now().date() > self.last_check_date:
            self.daily_loss = 0.0
            self.last_check_date = datetime.now().date()
        
        self.daily_loss += daily_loss
        
        if self.daily_loss <= -self.config.daily_loss_limit:
            logger.critical(f"Daily loss limit exceeded: {self.daily_loss:.2f}")
            self.trip()
    
    def emergency_stop(self) -> None:
        """
        Immediate emergency stop.
        """
        self.trip()
        logger.critical("EMERGENCY STOP ACTIVATED - All trading halted immediately")
