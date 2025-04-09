#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Binance Trading Bot with QQE Indicator

This is the main entry point for the trading bot application.
It initializes the bot with configuration settings and starts the trading process.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import NoReturn

from src.bot import TradingBot
from src.config import (
    DEFAULT_MODE,
    DEFAULT_TIMEFRAME,
    LOG_LEVEL,
    MODE_BACKTEST,
    MODE_LIVE,
    MODE_PAPER,
    TRADING_PAIRS,
)
from src.logger import setup_logger

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Binance Trading Bot with QQE Indicator")
    parser.add_argument(
        "--mode",
        type=str,
        choices=[MODE_BACKTEST, MODE_PAPER, MODE_LIVE],
        default=DEFAULT_MODE,
        help="Trading mode: backtest, paper, or live",
    )
    parser.add_argument(
        "--pair",
        type=str,
        default=TRADING_PAIRS[0],
        help="Trading pair (e.g., BTCUSDT)",
    )
    parser.add_argument(
        "--timeframe",
        type=str,
        default=DEFAULT_TIMEFRAME,
        help="Trading timeframe",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default=LOG_LEVEL,
        help="Logging level",
    )
    return parser.parse_args()


def main() -> NoReturn:
    """Main entry point for the trading bot."""
    # Parse command line arguments
    args: argparse.Namespace = parse_arguments()

    # Setup logger
    logger: logging.Logger = setup_logger(args.log_level)
    logger.info("Starting Binance Trading Bot with QQE Indicator")
    logger.info("Mode: %s, Pair: %s, Timeframe: %s", args.mode, args.pair, args.timeframe)

    try:
        # Initialize and run the trading bot
        bot: TradingBot = TradingBot(
            trading_pair=args.pair,
            timeframe=args.timeframe,
            mode=args.mode,
        )
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception("An error occurred: %s", e)
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()
