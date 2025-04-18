#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Coin-M Futures Runner for Binance Trading Bot.

This script provides a command-line interface for running the
QQE trading strategy on Binance Futures Coin-M markets.
"""

import argparse
import logging

from src.bot.futures import CoinMFuturesBot
from src.config import (
    DEFAULT_TIMEFRAME,
    FUTURES_TRADING_PAIRS,
    LOG_LEVEL,
    MODE_LIVE,
    MODE_PAPER,
)
from src.logger import setup_logger


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Coin-M Futures Runner for Binance Trading Bot")
    parser.add_argument(
        "--mode",
        type=str,
        choices=[MODE_PAPER, MODE_LIVE],
        default=MODE_PAPER,
        help="Trading mode: paper or live",
    )
    parser.add_argument(
        "--pair",
        type=str,
        default=FUTURES_TRADING_PAIRS[0],
        help="Trading pair (e.g., BTCUSD_PERP)",
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


def main() -> None:
    """Main entry point for the Coin-M futures runner."""
    # Parse command line arguments
    args: argparse.Namespace = parse_arguments()

    # Setup logger
    logger: logging.Logger = setup_logger(args.log_level)
    logger.info("Starting Coin-M Futures Runner for Binance Trading Bot with QQE Indicator")
    logger.info("Mode: %s, Pair: %s, Timeframe: %s", args.mode, args.pair, args.timeframe)

    try:
        # Initialize and run the trading bot
        bot = CoinMFuturesBot(
            trading_pair=args.pair,
            timeframe=args.timeframe,
            mode=args.mode,
        )
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except (ConnectionError, TimeoutError) as e:
        logger.exception("An error occurred: %s", e)
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()
