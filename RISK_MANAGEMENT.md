# Risk Management Guide

## Risk Management Fundamentals

Proper risk management is critical for long-term trading success. The engine includes comprehensive risk controls.

## Key Risk Limits

### 1. Position Sizing

**Max Position Size:** Maximum capital allocation per trade
```yaml
max_position_size: 0.1  # 10% of portfolio per trade
```

**Calculation:**
- Total Portfolio: $10,000
- Max per trade: $1,000 (10%)
- This limits single-trade losses

**Best Practice:** Use 1-5% for conservative trading, 5-10% for aggressive.

### 2. Stop Loss

**Purpose:** Limits losses on adverse trades

```yaml
stop_loss_percent: 2.0  # 2% below entry
```

**Example:**
- Entry: $100
- Stop Loss: $98 (2% loss)
- Maximum loss per trade: $1,000 * 0.02 = $20

**Levels by Strategy:**
- Momentum: 2-3%
- Mean Reversion: 2-2.5%
- Grid Trading: 3-5%
- DCA: 5-10%
- Arbitrage: 0.5-1%

### 3. Take Profit

**Purpose:** Locks in gains at target levels

```yaml
take_profit_percent: 5.0  # 5% above entry for buy
```

**Risk/Reward Ratio:**
- Target 1:2 or better (risk $100 to make $200)
- Example: 2% stop, 5% target = 1:2.5 ratio ✓

### 4. Maximum Drawdown

**Purpose:** Stops trading if portfolio declines too much

```yaml
max_drawdown_percent: 10.0  # Stop if 10% down from peak
```

**Scenario:**
- Peak balance: $10,000
- Current balance: $9,000
- Drawdown: 10% → Trading pauses
- Reset: After 24 hours or manual restart

### 5. Daily Loss Limit

**Purpose:** Prevents over-trading on losing days

```yaml
daily_loss_limit: 1000.0  # Stop after $1000 loss per day
```

**Timeline:**
- Resets at midnight UTC
- Cumulative losses tracked
- Trading halts when limit reached

### 6. Maximum Open Positions

**Purpose:** Limits portfolio concentration

```yaml
max_open_positions: 5  # Maximum simultaneous trades
```

**Portfolio Heat Example:**
- 5 positions × 10% each = 50% portfolio risk
- Recommended: 3-5 maximum for most traders

## Risk Assessment Framework

### Conservative Setup

For beginners or low risk tolerance:

```yaml
risk_management:
  max_position_size: 0.02        # 2% per trade
  stop_loss_percent: 3.0         # 3% stops
  max_drawdown_percent: 5.0      # Stop at 5% down
  daily_loss_limit: 200.0        # Tight daily limit
  max_open_positions: 3          # Few simultaneous trades
```

### Moderate Setup

For experienced traders:

```yaml
risk_management:
  max_position_size: 0.05        # 5% per trade
  stop_loss_percent: 2.0         # 2% stops
  max_drawdown_percent: 10.0     # 10% drawdown limit
  daily_loss_limit: 500.0        # Reasonable daily limit
  max_open_positions: 5          # Multiple positions
```

### Aggressive Setup

For professional traders only:

```yaml
risk_management:
  max_position_size: 0.10        # 10% per trade
  stop_loss_percent: 1.5         # 1.5% stops
  max_drawdown_percent: 20.0     # 20% drawdown limit
  daily_loss_limit: 1000.0       # Higher daily limit
  max_open_positions: 10         # Many simultaneous positions
```

## Risk Metrics

### Before Trading

Evaluate backtest results:

```json
{
  "win_rate": 55,                    // % of profitable trades
  "profit_factor": 2.5,              // Gross profit / Gross loss
  "max_drawdown": 8.5,               // Maximum peak-to-trough %
  "return_percent": 25.0,            // Total return %
  "avg_trade_duration": 240          // Minutes per trade
}
```

**Minimum Acceptable Standards:**
- Win Rate: > 45%
- Profit Factor: > 1.5
- Max Drawdown: < 15%
- Return: > 10% annually

### During Trading

Monitor daily:

```bash
# Check current portfolio heat
python -c "from src.core.engine import TradingEngine; 
e = TradingEngine(); print(e.get_summary())"
```

**Key Metrics:**
- Current Drawdown
- Daily Loss
- Open Positions
- Portfolio Heat
- P&L

## Portfolio Heat Tracking

**Definition:** Total portfolio exposure across all positions

**Calculation:**
```
Portfolio Heat = Sum of (Position Size × Leverage)
```

**Example:**
- Position 1: $1,000 (10% of portfolio)
- Position 2: $500 (5% of portfolio)
- Position 3: $1,500 (15% of portfolio)
- **Total Heat:** 30%

**Guidelines:**
- Minimum: 10-20% (underutilized)
- Optimal: 40-70% (balanced)
- Maximum: 100%+ (over-leveraged)

## Slippage Management

**Definition:** Difference between expected and actual execution price

```yaml
max_slippage_percent: 0.5  # Reject orders with > 0.5% slippage
```

**Factors:**
- Market conditions (high volatility = more slippage)
- Trade size (larger orders = more slippage)
- Liquidity (less liquid pairs = more slippage)

## Commission & Fees

**Binance Fees (Typical):**
- Maker: 0.1%
- Taker: 0.1%
- Total per round trip: 0.2%

**Impact on Strategy:**
- Minimum profit target must exceed fees
- Arbitrage requires spread > fees
- High-frequency strategies ineffective

## Volatility Adjustments

Adjust position size based on market volatility:

```python
# High volatility (ATR > 3%): Reduce position size by 50%
# Normal volatility (ATR 1-3%): Normal position size
# Low volatility (ATR < 1%): Can increase by 25%
```

## Correlation Risk

**Diversification:**
- Don't trade only correlated pairs
- Mix different assets (BTC, ETH, ALT)
- Reduces portfolio risk

**Example Dangerous Setup:**
- Only BTC trading
- All strategies on same timeframe
- Same market conditions affect all

**Better Setup:**
- BTC momentum (1h)
- ETH mean reversion (4h)
- ALT DCA (1d)
- Different conditions for each

## Emergency Controls

### Manual Shutdown

```bash
# Stop all trading immediately
python -c "import sys; sys.exit(1)"

# Or press Ctrl+C
```

### Circuit Breakers

**Automatic triggers:**
- Max drawdown → Stop trading
- Daily loss limit → Stop trading
- API errors → Reconnect with backoff
- Unusual market conditions → Manual review

## Compliance & Auditing

### Trade Logging

All trades logged to:
- `logs/trading_YYYY-MM-DD.log`
- `backtest_results.json`
- Portfolio history (optional)

### Required Checks

Before live trading:
1. ✓ Backtest 3+ months of data
2. ✓ Paper trade 2+ weeks
3. ✓ Monitor risk metrics daily
4. ✓ Review strategy logic
5. ✓ Verify API keys (read-only initially)
6. ✓ Test stop losses manually
7. ✓ Document decision rules

## Common Risk Mistakes

❌ **Mistake:** No stop losses
✓ **Solution:** Always set stops (2-3% default)

❌ **Mistake:** Position sizing too large
✓ **Solution:** Stick to 1-5% per trade

❌ **Mistake:** No daily limits
✓ **Solution:** Set daily loss limit (e.g., $500)

❌ **Mistake:** Averaging down
✓ **Solution:** Disable in configuration

❌ **Mistake:** Overtrading
✓ **Solution:** Limit max open positions

❌ **Mistake:** No backtesting
✓ **Solution:** Always backtest first

## Quick Risk Checklist

- [ ] Position size ≤ 5% per trade
- [ ] Stop loss set (2-3% typical)
- [ ] Take profit target set (≥ 1:2 ratio)
- [ ] Max open positions limited (3-5)
- [ ] Daily loss limit set ($200-1000)
- [ ] Max drawdown configured (5-10%)
- [ ] Backtested 3+ months
- [ ] Paper traded 2+ weeks
- [ ] API keys verified (read-only test first)
- [ ] Logs monitored daily

## Support & Resources

- Risk Calculator: See `src/utils/helpers.py`
- Risk Manager: See `src/core/risk_manager.py`
- Configuration: `config/risk.yaml`
- Questions: Issues & Discussions on GitHub
