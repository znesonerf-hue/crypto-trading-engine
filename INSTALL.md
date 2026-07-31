# Installation Guide

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git
- Binance account (for API keys)

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

Edit `.env` and add your Binance API credentials:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
TRADING_MODE=paper
INITIAL_CAPITAL=10000
```

### 5. Verify Installation

```bash
python -c "import src; print('Installation successful!')"
```

## Getting Binance API Keys

1. Log in to your Binance account at https://www.binance.com
2. Navigate to **Account** > **API Management**
3. Create a new API key with these permissions:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
   - ❌ Do NOT enable withdrawal
4. Copy API Key and Secret Key
5. Add to `.env` file

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
docker run -e BINANCE_API_KEY=xxx -e BINANCE_API_SECRET=yyy \
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

### API Connection Issues

1. Verify API keys are correct in `.env`
2. Check Binance API status at https://www.binance.com/en/support
3. Ensure your IP is whitelisted (if using IP restrictions)
4. For testnet, use `TRADING_MODE=paper` initially

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
