"""Configuration management"""

import os
from pathlib import Path
from typing import Any, Dict
import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for trading engine"""
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file
        """
        # Load environment variables
        load_dotenv(env_file)
        
        # API Configuration
        self.binance_api_key = os.getenv("BINANCE_API_KEY", "")
        self.binance_api_secret = os.getenv("BINANCE_API_SECRET", "")
        
        # Trading Configuration
        self.trading_mode = os.getenv("TRADING_MODE", "paper").lower()
        self.initial_capital = float(os.getenv("INITIAL_CAPITAL", "10000"))
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        self.log_file = os.getenv("LOG_FILE", "logs/trading.log")
        
        # Strategy Configuration
        self.default_strategy = os.getenv("DEFAULT_STRATEGY", "momentum")
        self.default_symbol = os.getenv("DEFAULT_SYMBOL", "BTCUSDT")
        self.default_timeframe = os.getenv("DEFAULT_TIMEFRAME", "1h")
        
        # Paper Trading
        self.paper_trading_enabled = os.getenv("PAPER_TRADING_ENABLED", "true").lower() == "true"
        self.slippage_percent = float(os.getenv("SLIPPAGE_PERCENT", "0.1"))
        
        # Risk Management
        self.max_position_size = float(os.getenv("MAX_POSITION_SIZE", "0.1"))
        self.stop_loss_percent = float(os.getenv("STOP_LOSS_PERCENT", "2.0"))
        self.max_drawdown_percent = float(os.getenv("MAX_DRAWDOWN_PERCENT", "10.0"))
        self.daily_loss_limit = float(os.getenv("DAILY_LOSS_LIMIT", "1000.0"))
        self.max_open_positions = int(os.getenv("MAX_OPEN_POSITIONS", "5"))
        
        # Notifications
        self.telegram_token = os.getenv("TELEGRAM_TOKEN", "")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
        self.discord_webhook_url = os.getenv("DISCORD_WEBHOOK_URL", "")
    
    def load_strategy_config(self, config_file: str = "config/strategies.yaml") -> Dict[str, Any]:
        """
        Load strategy configuration from YAML file.
        
        Args:
            config_file: Path to strategies config file
        
        Returns:
            Strategy configuration dictionary
        """
        if not Path(config_file).exists():
            return {}
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def load_risk_config(self, config_file: str = "config/risk.yaml") -> Dict[str, Any]:
        """
        Load risk management configuration from YAML file.
        
        Args:
            config_file: Path to risk config file
        
        Returns:
            Risk configuration dictionary
        """
        if not Path(config_file).exists():
            return {}
        
        with open(config_file, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def validate(self) -> bool:
        """
        Validate configuration for trading mode.
        
        Returns:
            True if valid, raises exception otherwise
        """
        if self.trading_mode not in ["paper", "backtest", "live"]:
            raise ValueError(f"Invalid trading mode: {self.trading_mode}")
        
        if self.trading_mode == "live":
            if not self.binance_api_key or not self.binance_api_secret:
                raise ValueError("Live trading requires API credentials")
        
        if self.initial_capital <= 0:
            raise ValueError("Initial capital must be positive")
        
        return True


# Global config instance
config = Config()
