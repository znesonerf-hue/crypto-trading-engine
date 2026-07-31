# Strategies Guide

## Momentum Strategy

**Description:** Follows price trends using moving averages and RSI.

**How It Works:**
1. Calculates fast (20) and slow (50) moving averages
2. Checks RSI for overbought/oversold conditions
3. Confirms volume surge
4. Buys when fast MA > slow MA and RSI < overbought
5. Sells when fast MA < slow MA

**Parameters:**
```yaml
fast_ma: 20              # Fast moving average period
slow_ma: 50             # Slow moving average period
rsi_period: 14          # RSI calculation period
rsi_overbought: 70      # Overbought threshold
rsi_oversold: 30        # Oversold threshold
min_volume_ratio: 1.2   # Minimum volume vs average
stop_loss_percent: 2.0
take_profit_percent: 5.0
```

**Best For:**
- Trending markets
- Longer timeframes (1h, 4h)
- Clear directional moves

**Risks:**
- Whipsaws in range-bound markets
- Delayed entries in fast moves

---

## Mean Reversion Strategy

**Description:** Exploits price deviations from moving averages using Bollinger Bands.

**How It Works:**
1. Calculates Bollinger Bands (20-period SMA ± 2 std)
2. Buys when price touches lower band and recovers
3. Sells when price touches upper band
4. Validates band width before trading

**Parameters:**
```yaml
bb_period: 20           # Bollinger Band period
bb_std_dev: 2.0         # Standard deviations
rsi_period: 14          # Additional RSI confirmation
stop_loss_percent: 2.5
take_profit_percent: 4.0
```

**Best For:**
- Range-bound/volatile markets
- Mean reversion corrections
- Medium timeframes (4h, 8h)

**Risks:**
- Fails in strong trending markets
- Requires tight stops

---

## Grid Trading Strategy

**Description:** Automated buying and selling at predefined price levels.

**How It Works:**
1. Establishes grid around current price
2. Places buy orders below current price
3. Places sell orders above current price
4. Executes when price crosses levels
5. Works best in sideways markets

**Parameters:**
```yaml
grid_levels: 5              # Number of grid levels
grid_range_percent: 5.0     # Grid range as % of price
entry_side: both            # 'long', 'short', or 'both'
stop_loss_percent: 3.0      # Overall stop loss
```

**Best For:**
- Range-bound markets
- Accumulation strategies
- Systematic profit taking

**Risks:**
- Limited profit in strong trends
- Requires capital for all levels

---

## Dollar Cost Averaging (DCA)

**Description:** Systematic accumulation strategy buying fixed amounts at intervals.

**How It Works:**
1. Buys fixed amount (e.g., $100) at regular intervals
2. Reduces impact of volatility
3. Builds position over time
4. Minimizes timing risk

**Parameters:**
```yaml
dca_amount: 100             # Amount per purchase (USDT)
dca_interval_hours: 24      # Hours between purchases
max_position_value: 10000   # Maximum total position
stop_loss_percent: 10.0     # Wider stop for DCA
```

**Best For:**
- Long-term accumulation
- Reducing volatility impact
- Consistent execution

**Risks:**
- Slow capital deployment
- Limited in falling markets

---

## Arbitrage Strategy

**Description:** Exploits price differences across pairs or exchanges.

**How It Works:**
1. Monitors correlated pairs (e.g., BTC/USDT vs BTC/BUSD)
2. Detects spread deviations
3. Buys undervalued, sells overvalued
4. Closes position when spread normalizes

**Parameters:**
```yaml
arbitrage_symbols: []          # Pairs to monitor
min_spread_percent: 0.5         # Minimum spread to trade
correlation_threshold: 0.8      # Minimum correlation
stop_loss_percent: 1.0          # Tight stops for arb
```

**Best For:**
- Pairs with consistent spreads
- Cross-exchange opportunities
- Low-risk, steady returns

**Risks:**
- Requires fast execution
- Small profit margins
- Liquidity constraints

---

## Strategy Selection Guide

| Strategy | Trend | Range | Volatility | Skill | Capital |
|----------|-------|-------|------------|-------|----------|
| Momentum | ⭐⭐⭐ | ⭐ | ⭐⭐ | Medium | Medium |
| Mean Reversion | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Medium | Medium |
| Grid Trading | ⭐ | ⭐⭐⭐ | ⭐ | Low | High |
| DCA | ⭐⭐ | ⭐⭐ | ⭐⭐⭐ | Low | Medium |
| Arbitrage | ⭐⭐ | ⭐⭐ | ⭐ | High | High |

## Performance Comparison

**Expected Returns (Historical Averages):**

- **Momentum:** 15-30% annually (trending markets)
- **Mean Reversion:** 10-20% annually (range-bound markets)
- **Grid Trading:** 5-15% annually (stable range)
- **DCA:** 8-12% annually (long-term)
- **Arbitrage:** 1-5% per trade (high frequency)

## Combining Strategies

Run multiple strategies on different symbols:

```bash
# Create custom runner
python -c "
from src.core.engine import TradingEngine
from src.strategies.momentum import MomentumStrategy
from src.strategies.dca import DCAStrategy

engine = TradingEngine(mode='paper', initial_capital=50000)
engine.add_strategy(MomentumStrategy('BTCUSDT', '1h'))
engine.add_strategy(DCAStrategy('ETHUSDT', '1d'))
engine.run()
"
```

## Optimization

### Backtesting Parameters

```bash
# Test different MA periods
for fast in 10 15 20; do
  for slow in 40 50 60; do
    python backtest.py --strategy momentum \
      --params '{"fast_ma": '$fast', "slow_ma": '$slow'}'
  done
done
```

### Performance Metrics

After backtesting, focus on:
- **Win Rate:** Percentage of profitable trades
- **Profit Factor:** Gross profits / Gross losses
- **Drawdown:** Maximum peak-to-trough decline
- **Sharpe Ratio:** Risk-adjusted returns

## Next Steps

1. Start with momentum on 1h timeframe
2. Backtest 3-6 months of data
3. Paper trade for 2-4 weeks
4. Monitor performance metrics
5. Adjust parameters based on results
6. Only move to live trading after consistent profits
