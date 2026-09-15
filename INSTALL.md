# Installation Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/znesonerf-hue/crypto-trading-engine.git
cd crypto-trading-engine
```

### 2. Create Virtual Environment

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example configuration:
```bash
cp .env.example .env
```

Edit `.env` - CoinGecko requires no API key for free tier:
```
# Optional: Add CoinGecko Pro API key for higher rate limits
COINGECKO_API_KEY=your_optional_pro_key

# Trading Configuration
TRADING_MODE=paper
INITIAL_CAPITAL=10000
```

### 5. Verify Installation

```bash
python -c "import src; print('Installation successful!')"
```

## CoinGecko API Setup

The crypto trading engine uses **CoinGecko API** for cryptocurrency data.

### Free Tier (Recommended for most users)
- No API key required
- Rate limit: 10-50 requests/minute
- Updates: ~30 seconds delayed
- Perfect for swing trading and backtesting

### Pro Tier (Optional)
1. Sign up at https://www.coingecko.com/en/api
2. Create Pro account for higher rate limits
3. Get your API key from dashboard
4. Add to `.env`: `COINGECKO_API_KEY=your_key_here`

## Docker Installation

### Using Docker Compose

```bash
# Build image
docker-compose build

# Run container
docker-compose up -d

# View logs
docker-compose logs -f trading-bot

# Stop container
docker-compose down
```

### Using Docker CLI

```bash
# Build image
docker build -t crypto-trading-engine .

# Run container
docker run -e TRADING_MODE=paper \
  -v $(pwd)/logs:/app/logs \
  crypto-trading-engine
```

## Troubleshooting

### Import Errors

```bash
# Verify PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Reinstall packages
pip install --upgrade -r requirements.txt
```

### CoinGecko API Connection Issues

1. Verify internet connection
2. Check CoinGecko status at https://www.coingecko.com/
3. For Pro tier, verify API key in `.env`
4. Rate limits exceeded? Pro tier offers higher limits

### Permission Errors

```bash
# Create logs directory
mkdir -p logs

# Set permissions
chmod 755 logs
```

## Next Steps

1. Read [QUICKSTART.md](QUICKSTART.md) for basic usage
2. Review [STRATEGIES.md](STRATEGIES.md) for strategy details
3. Check [RISK_MANAGEMENT.md](RISK_MANAGEMENT.md) for risk settings
4. Run backtests before paper trading
