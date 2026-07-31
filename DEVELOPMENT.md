# Development Guide

## Project Structure

```
crypto-trading-engine/
├── src/
│   ├── core/              # Core trading logic
│   │   ├── engine.py      # Main trading engine
│   │   ├── portfolio.py   # Portfolio tracking
│   │   └── risk_manager.py
│   ├── strategies/        # Trading strategies
│   │   ├── base.py        # Strategy interface
│   │   ├── momentum.py
│   │   ├── mean_reversion.py
│   │   ├── grid_trading.py
│   │   ├── arbitrage.py
│   │   └── dca.py
│   ├── connectors/        # Exchange connectors
│   │   └── binance.py
│   ├── data/              # Data handling
│   ├── backtest/          # Backtesting
│   └── utils/             # Utilities
├── config/                # Configuration files
├── tests/                 # Test suite
├── main.py                # Paper trading entry
└── backtest.py            # Backtesting entry
```

## Creating New Strategies

### 1. Extend BaseStrategy

```python
from src.strategies.base import BaseStrategy, Signal
import pandas as pd

class MyStrategy(BaseStrategy):
    def __init__(self, symbol: str, timeframe: str, params=None):
        default_params = {
            'param1': 20,
            'param2': 50,
            'stop_loss_percent': 2.0,
            'take_profit_percent': 5.0
        }
        if params:
            default_params.update(params)
        super().__init__(symbol, timeframe, default_params)
    
    def calculate_signal(self, data: pd.DataFrame) -> Signal:
        """Implement your trading logic here"""
        # Your indicator calculations
        # Return Signal.BUY, Signal.SELL, or Signal.HOLD
        pass
    
    def validate_signal(self, data: pd.DataFrame, signal: Signal) -> bool:
        """Validate signal with additional checks"""
        # Extra validation logic
        return True
```

### 2. Implement Required Methods

Every strategy must implement:
- `calculate_signal()` - Core logic
- `validate_signal()` - Validation rules
- Optionally: `get_entry_price()`, `get_stop_loss()`, `get_take_profit()`

### 3. Test Your Strategy

```python
import pytest
import pandas as pd
from src.strategies.my_strategy import MyStrategy

class TestMyStrategy:
    def test_signal_calculation(self):
        strategy = MyStrategy('BTCUSDT', '1h')
        # Create test data
        data = pd.DataFrame({
            'close': [100, 101, 102, 101, 100],
            'volume': [1000, 1100, 1200, 1100, 1000]
        })
        signal = strategy.calculate_signal(data)
        assert signal in [Signal.BUY, Signal.SELL, Signal.HOLD]
```

### 4. Add to Configuration

Update `config/strategies.yaml`:

```yaml
strategies:
  my_strategy:
    enabled: true
    symbol: BTCUSDT
    timeframe: 1h
    parameters:
      param1: 20
      param2: 50
```

### 5. Use Your Strategy

```python
from src.core.engine import TradingEngine
from src.strategies.my_strategy import MyStrategy

engine = TradingEngine(mode='paper')
strategy = MyStrategy('BTCUSDT', '1h')
engine.add_strategy(strategy)
engine.run()
```

## Adding New Indicators

### 1. Add to helpers.py

```python
def calculate_my_indicator(data: pd.Series, period: int) -> pd.Series:
    """Calculate custom indicator"""
    # Your calculation logic
    return result
```

### 2. Use in Strategy

```python
from src.utils.helpers import calculate_my_indicator

class MyStrategy(BaseStrategy):
    def calculate_signal(self, data: pd.DataFrame) -> Signal:
        indicator = calculate_my_indicator(data['close'], self.params['period'])
        # Use indicator values...
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_strategies.py::TestMomentumStrategy -v
```

### Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Structure

```python
class TestMyStrategy:
    @pytest.fixture
    def strategy(self):
        return MyStrategy('BTCUSDT', '1h')
    
    def test_initialization(self, strategy):
        assert strategy.symbol == 'BTCUSDT'
    
    def test_signal_on_uptrend(self, strategy):
        # Test BUY signal in uptrend
        pass
    
    def test_signal_on_downtrend(self, strategy):
        # Test SELL signal in downtrend
        pass
```

## Code Style

### Naming Conventions

```python
# Classes: PascalCase
class TradingEngine: pass

# Functions/methods: snake_case
def calculate_signal(): pass

# Constants: UPPER_CASE
MAX_POSITION_SIZE = 0.1

# Private: _leading_underscore
def _execute_trade(): pass
```

### Documentation

Every function needs docstring:

```python
def calculate_signal(self, data: pd.DataFrame) -> Signal:
    """
    Calculate trading signal based on data.
    
    Args:
        data: OHLCV data as DataFrame
    
    Returns:
        Trading signal (BUY, SELL, or HOLD)
    
    Raises:
        ValueError: If data is invalid
    """
    pass
```

## Debugging

### Enable Debug Logging

```bash
# In .env
LOG_LEVEL=DEBUG
```

### Add Debug Prints

```python
from src.utils.logger import setup_logger
logger = setup_logger(__name__)

logger.debug(f"Variable value: {value}")
logger.info(f"Strategy signal: {signal}")
logger.warning(f"Potential issue: {issue}")
logger.error(f"Error occurred: {error}")
```

### Interactive Debugging

```python
import pdb; pdb.set_trace()  # Debugger breakpoint
```

## Performance Optimization

### Profiling

```bash
python -m cProfile -s cumulative main.py --mode paper
```

### Memory Usage

```python
import tracemalloc
tracemalloc.start()
# ... your code ...
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024 / 1024:.2f} MB")
print(f"Peak: {peak / 1024 / 1024:.2f} MB")
```

## Contributing

1. Fork repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make changes and test
4. Commit: `git commit -am 'Add my feature'`
5. Push: `git push origin feature/my-feature`
6. Create Pull Request

## Deployment

### Local Deployment

```bash
python main.py --mode paper --strategy momentum
```

### Docker Deployment

```bash
docker-compose up -d
```

### Cloud Deployment (AWS Example)

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin xxx.dkr.ecr.us-east-1.amazonaws.com

docker build -t crypto-trading-engine .
docker tag crypto-trading-engine:latest xxx.dkr.ecr.us-east-1.amazonaws.com/crypto-trading-engine:latest
docker push xxx.dkr.ecr.us-east-1.amazonaws.com/crypto-trading-engine:latest

# Run on EC2 or ECS
```

## Troubleshooting

### ImportError

```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### API Errors

```python
try:
    data = connector.get_klines(symbol, timeframe)
except BinanceAPIException as e:
    logger.error(f"API Error: {e.status_code} - {e.message}")
```

### No Signals Generated

- Check data availability
- Verify indicator calculations
- Review signal logic
- Run backtest with DEBUG logging

## Resources

- Python: https://docs.python.org/3/
- Pandas: https://pandas.pydata.org/docs/
- Binance API: https://binance-docs.github.io/apidocs/
- Technical Analysis: https://school.stockcharts.com/

## License

MIT - See LICENSE file
