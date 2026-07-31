# Quick Start Guide

## Running Paper Trading

### Basic Usage

```bash
# Run momentum strategy on BTCUSDT (default)
python main.py --mode paper --strategy momentum

# Run on different symbol
python main.py --mode paper --strategy momentum --symbol ETHUSDT

# Adjust update interval (seconds)
python main.py --mode paper --strategy momentum --interval 30

# Set initial capital
python main.py --mode paper --strategy momentum --capital 50000
```

### Available Strategies

```bash
# Momentum Trading (trend following)
python main.py --strategy momentum --symbol BTCUSDT

# Mean Reversion (buying dips)
python main.py --strategy mean_reversion --symbol ETHUSDT

# Grid Trading (automated levels)
python main.py --strategy grid --symbol BNBUSDT

# Dollar Cost Averaging (systematic buying)
python main.py --strategy dca --symbol BTCUSDT

# Arbitrage (cross-pair spreads)
python main.py --strategy arbitrage --symbol BTCUSDT
```

## Running Backtests

### Basic Backtest

```bash
# Backtest momentum strategy for 3 months
python backtest.py --strategy momentum \
  --start-date 2024-01-01 \
  --end-date 2024-03-31
```

### Advanced Backtest

```bash
# Backtest on different symbol with custom capital
python backtest.py --strategy mean_reversion \
  --symbol ETHUSDT \
  --start-date 2024-01-01 \
  --end-date 2024-12-31 \
  --capital 25000 \
  --output results.json
```

### Backtest Multiple Strategies

```bash
# Run backtests for all strategies
for strategy in momentum mean_reversion grid dca; do
  echo "Testing $strategy..."
  python backtest.py --strategy $strategy \
    --start-date 2024-01-01 \
    --end-date 2024-12-31
done
```

## Configuration

### Strategy Parameters

Edit `config/strategies.yaml` to customize strategy settings:

```yaml
strategies:
  momentum:
    enabled: true
    symbol: BTCUSDT
    timeframe: 1h
    parameters:
      fast_ma: 20      # Fast moving average period
      slow_ma: 50      # Slow moving average period
      rsi_period: 14   # RSI period
      rsi_overbought: 70
      rsi_oversold: 30
```

### Risk Management

Edit `config/risk.yaml` to adjust risk limits:

```yaml
risk_management:
  max_position_size: 0.1      # 10% per position
  max_open_positions: 5       # Max concurrent positions
  max_drawdown_percent: 10.0  # Stop if 10% down
  daily_loss_limit: 1000.0    # Stop after $1000 loss
```

## Monitoring

### View Logs

```bash
# Real-time logs
tail -f logs/trading_*.log

# View specific date
cat logs/trading_2024-07-31.log

# Filter by level
grep "ERROR" logs/trading_*.log
grep "WARNING" logs/trading_*.log
```

### Performance Metrics

After backtesting, check `backtest_results.json`:

```bash
# Pretty print results
python -m json.tool backtest_results.json

# Extract key metrics
jq '.total_trades, .win_rate, .total_pnl' backtest_results.json
```

## Common Issues

### No Trades Generated

- Backtest period may not have signals
- Strategy parameters may be too strict
- Check historical price action in selected period

### API Connection Errors

- Verify `BINANCE_API_KEY` and `BINANCE_API_SECRET` in `.env`
- Check internet connection
- Ensure IP is whitelisted (if restricted on Binance)

### Insufficient Balance

- Reduce `INITIAL_CAPITAL` in configuration
- Reduce `max_position_size` percentage
- Lower `dca_amount` for DCA strategy

## Next Steps

1. Review [STRATEGIES.md](STRATEGIES.md) for detailed strategy info
2. Learn about [RISK_MANAGEMENT.md](RISK_MANAGEMENT.md)
3. Check [DEVELOPMENT.md](DEVELOPMENT.md) for customization

## Support

- Issues: https://github.com/znesonerf-hue/crypto-trading-engine/issues
- Discussions: https://github.com/znesonerf-hue/crypto-trading-engine/discussions
- Email: znesonerf@gmail.com
