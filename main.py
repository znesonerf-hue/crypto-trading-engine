"""Main entry point for paper trading"""

import argparse
from src.core.engine import TradingEngine
from src.strategies.momentum import MomentumStrategy
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.grid_trading import GridTradingStrategy
from src.strategies.arbitrage import ArbitrageStrategy
from src.strategies.dca import DCAStrategy
from src.utils.config import config
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """
    Main entry point for paper trading.
    """
    parser = argparse.ArgumentParser(description="Crypto Trading Engine - Paper Trading")
    parser.add_argument("--mode", default="paper", choices=["paper", "live"],
                       help="Trading mode")
    parser.add_argument("--strategy", default="momentum",
                       choices=["momentum", "mean_reversion", "grid", "arbitrage", "dca"],
                       help="Strategy to run")
    parser.add_argument("--symbol", default="BTCUSDT", help="Trading symbol")
    parser.add_argument("--capital", type=float, default=10000, help="Initial capital")
    parser.add_argument("--interval", type=int, default=60, help="Update interval in seconds")
    
    args = parser.parse_args()
    
    # Initialize engine
    engine = TradingEngine(mode=args.mode, initial_capital=args.capital)
    
    # Add selected strategy
    if args.strategy == "momentum":
        strategy = MomentumStrategy(args.symbol, "1h")
    elif args.strategy == "mean_reversion":
        strategy = MeanReversionStrategy(args.symbol, "4h")
    elif args.strategy == "grid":
        strategy = GridTradingStrategy(args.symbol, "1h")
    elif args.strategy == "arbitrage":
        strategy = ArbitrageStrategy(args.symbol, "15m")
    elif args.strategy == "dca":
        strategy = DCAStrategy(args.symbol, "1d")
    else:
        logger.error(f"Unknown strategy: {args.strategy}")
        return
    
    engine.add_strategy(strategy)
    
    # ตั้งค่าให้ logging แสดงเวลาและระดับความสำคัญ
    logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def run_bot_loop():
  while True:
    logging.info("Bot กำลังทำงานรอบปัจจุบัน... สถานะปกติสุขดี")

    # โค้ดงานของคุณตรงนี้ (เช่น ดึงข้อมูล หรือเทรด)
    # ...

    logging.info("พักการทำงาน 60 วินาทีก่อนเริ่มรอบถัดไป...")
    time.sleep(60)  # พัก 1 นาทีแล้ววนลูปใหม่ (ปรับเวลาตามต้องการ)


if __name__ == "__main__":
  logging.info("เริ่มต้นเปิดระบบ Bot...")
  run_bot_loop()
    
    # Run engine
    try:
        logger.info(f"Starting trading engine: {args.strategy} on {args.symbol}")
        engine.run(interval_seconds=args.interval)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        engine.stop()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
    
    # Print summary
    summary = engine.get_summary()
    logger.info(f"Summary: {summary}")


if __name__ == "__main__":
    main()
