"""Main entry point for backtesting"""

import argparse
from src.backtest.engine import BacktestEngine
from src.strategies.momentum import MomentumStrategy
from src.strategies.mean_reversion import MeanReversionStrategy
from src.strategies.grid_trading import GridTradingStrategy
from src.strategies.dca import DCAStrategy
from src.utils.logger import setup_logger
import json

logger = setup_logger(__name__)


def main():
    """
    Main entry point for backtesting.
    """
    parser = argparse.ArgumentParser(description="Crypto Trading Engine - Backtesting")
    parser.add_argument("--strategy", required=True,
                       choices=["momentum", "mean_reversion", "grid", "dca"],
                       help="Strategy to backtest")
    parser.add_argument("--symbol", default="BTCUSDT", help="Trading symbol")
    parser.add_argument("--start-date", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", required=True, help="End date (YYYY-MM-DD)")
    parser.add_argument("--capital", type=float, default=10000, help="Initial capital")
    parser.add_argument("--output", default="backtest_results.json", help="Output file")
    
    args = parser.parse_args()
    
    # Initialize backtest engine
    engine = BacktestEngine(initial_capital=args.capital)
    
    # Create strategy
    if args.strategy == "momentum":
        strategy = MomentumStrategy(args.symbol, "1h")
    elif args.strategy == "mean_reversion":
        strategy = MeanReversionStrategy(args.symbol, "4h")
    elif args.strategy == "grid":
        strategy = GridTradingStrategy(args.symbol, "1h")
    elif args.strategy == "dca":
        strategy = DCAStrategy(args.symbol, "1d")
    else:
        logger.error(f"Unknown strategy: {args.strategy}")
        return
    
    # Run backtest
    logger.info(f"Running backtest: {args.strategy} on {args.symbol}")
    logger.info(f"Period: {args.start_date} to {args.end_date}")
    logger.info(f"Initial capital: ${args.capital}")
    
    results = engine.run_strategy(args.symbol, strategy, args.start_date, args.end_date)
    
    # Print results
    if results:
        logger.info("\n" + "="*60)
        logger.info("BACKTEST RESULTS")
        logger.info("="*60)
        logger.info(f"Total Trades: {results['total_trades']}")
        logger.info(f"Winning Trades: {results['winning_trades']}")
        logger.info(f"Losing Trades: {results['losing_trades']}")
        logger.info(f"Win Rate: {results['win_rate']:.2f}%")
        logger.info(f"Total P&L: ${results['total_pnl']:.2f}")
        logger.info(f"Return: {results['return_percent']:.2f}%")
        logger.info(f"Profit Factor: {results['profit_factor']:.2f}")
        logger.info(f"Max Drawdown: ${results['max_drawdown']:.2f}")
        logger.info(f"Avg Win: ${results['avg_win']:.2f}")
        logger.info(f"Avg Loss: ${results['avg_loss']:.2f}")
        logger.info("="*60)
        
        # Save results
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {args.output}")
    else:
        logger.error("Backtest failed or no trades generated")


if __name__ == "__main__":
    main()
