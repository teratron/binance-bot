#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Binance Trading Bot with QQE Indicator

This is the main entry point for the trading bot application.
It initializes the bot with configuration settings and starts the trading process.
"""

import argparse
import logging

from binance.spot import Spot  # type: ignore
from binance.websocket.spot.websocket_stream import BinanceWebsocketClient, SpotWebsocketStreamClient  # type: ignore

from config import (
    DEFAULT_MODE,
    DEFAULT_TIMEFRAME,
    LOG_LEVEL,
    MODE_BACKTEST,
    MODE_LIVE,
    MODE_PAPER,
    TRADING_PAIRS, )
from logger import setup_logger
# import sys
# from pathlib import Path
# Add the project root to the Python path before any imports
# project_root = Path(__file__).parent.parent
# sys.path.insert(0, str(project_root))
# if sys.path[0] == str(project_root):
from bot.bot import TradingBot


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(description="Binance Trading Bot")
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


def main() -> None:
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
    except (ConnectionError, TimeoutError) as e:
        logger.exception("An error occurred: %s", e)
    finally:
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    main()
    # api_key = os.getenv("BINANCE_API_KEY")
    # api_secret = os.getenv("BINANCE_API_SECRET")
    # base_url = os.getenv("BINANCE_BASE_URL")
    # client = Spot(api_key=api_key, api_secret=api_secret, base_url=base_url)
    # order = client.new_order(
    #     symbol="BTCUSDT",
    #     side="BUY",
    #     type="MARKET",
    #     quoteOrderQty=MAX_POSITION_SIZE,  # Amount in base currency
    # )
    # client = API(api_key=api_key, api_secret=api_secret, base_url=base_url)
    # client = SpotWebsocketStreamClient()
    # client.ping()
    # client.kline(symbol="BTCUSDT", interval="1m")
    # print(client)
    # client.stop()
