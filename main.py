#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Binance Trading Bot with QQE Indicator

This is the main entry point for the trading bot application.
It initializes the bot with configuration settings and starts the trading process.
"""

import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

import config
from src.bot.bot import TradingBot
from src.bot.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Binance Trading Bot with QQE Indicator")
    parser.add_argument(
        "--mode",
        type=str,
        choices=[config.MODE_BACKTEST, config.MODE_PAPER, config.MODE_LIVE],
        default=config.DEFAULT_MODE,
        help="Trading mode: backtest, paper, or live",
    )
    parser.add_argument(
        "--pair",
        type=str,
        default=config.TRADING_PAIRS[0],
        help="Trading pair (e.g., BTCUSDT)",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default=config.DEFAULT_TIMEFRAME,
        help="Trading timeframe",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=config.LOG_LEVEL,
        help="Logging level",
    )
    return parser.parse_args()


def main():
    """Main entry point for the trading bot."""
    # Parse command line arguments
    args = parse_arguments()

    # Setup logger
    logger = setup_logger(args.log_level)
    logger.info("Starting Binance Trading Bot with QQE Indicator")
    logger.info(f"Mode: {args.mode}, Pair: {args.pair}, Timeframe: {args.timeframe}")

    try:
        # Initialize and run the trading bot
        bot = TradingBot(
            trading_pair=args.pair,
            timeframe=args.timeframe,
            mode=args.mode,
        )
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()
