#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Backtest Runner for Binance Trading Bot.

This script provides a command-line interface for running backtests
of the QQE trading strategy on historical Binance data.
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, TypedDict, cast

from backtest import run_backtest
from config import (
    BACKTEST_END_DATE,
    BACKTEST_START_DATE,
    DEFAULT_TIMEFRAME,
    LOG_LEVEL,
    TRADING_PAIRS,
)
from logger import setup_logger


# Define TypedDict classes for backtest results structure
class TradeDict(TypedDict):
    """Type definition for a trade record."""

    side: str
    entry_price: float
    exit_price: float
    size: float
    entry_time: datetime
    exit_time: datetime
    profit_loss: float
    profit_loss_percent: float


class EquityPointDict(TypedDict):
    """Type definition for an equity curve point."""

    timestamp: datetime
    equity: float


class BacktestResultsDict(TypedDict):
    """Type definition for backtest results."""

    initial_balance: float
    final_balance: float
    total_return: float
    total_return_percent: float
    num_trades: int
    win_rate: float
    profit_factor: float
    max_drawdown: float
    max_drawdown_percent: float
    trades: List[TradeDict]
    equity_curve: List[EquityPointDict]
    summary: str


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Backtest Runner for Binance Trading Bot")
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
        "--start-date",
        type=str,
        default=BACKTEST_START_DATE,
        help="Start date for backtesting (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=BACKTEST_END_DATE,
        help="End date for backtesting (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--initial-balance",
        type=float,
        default=1000.0,
        help="Initial balance for backtesting",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file for backtest results (JSON format)",
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
    """Main entry point for the backtest runner."""
    # Parse command line arguments
    args: argparse.Namespace = parse_arguments()

    # Setup logger
    logger: logging.Logger = setup_logger(args.log_level)
    logger.info("Starting Backtest Runner for Binance Trading Bot with QQE Indicator")
    logger.info(
        "Pair: %s, Timeframe: %s, Period: %s to %s, Initial Balance: %s",
        args.pair,
        args.timeframe,
        args.start_date,
        args.end_date,
        args.initial_balance,
    )

    try:
        # Run backtest
        results: BacktestResultsDict = cast(
            BacktestResultsDict,
            run_backtest(
                trading_pair=args.pair,
                timeframe=args.timeframe,
                start_date=args.start_date,
                end_date=args.end_date,
                initial_balance=args.initial_balance,
            ),
        )

        # Print summary
        print("\nBacktest Results:")
        print(f"Trading Pair: {args.pair}")
        print(f"Timeframe: {args.timeframe}")
        print(f"Period: {args.start_date} to {args.end_date}")
        print(f"Initial Balance: {args.initial_balance}")
        print(f"Final Balance: {results['final_balance']:.2f}")
        print(
            f"Total Return: {results['total_return']:.2f} ({results['total_return_percent']:.2f}%)"
        )
        print(f"Number of Trades: {results['num_trades']}")
        print(f"Win Rate: {results['win_rate']:.2f}%")
        print(f"Profit Factor: {results['profit_factor']:.2f}")
        print(
            f"Max Drawdown: {results['max_drawdown']:.2f} ({results['max_drawdown_percent']:.2f}%)"
        )

        # Save results to file if specified
        if args.output:
            output_path: Path = Path(args.output)

            # Convert datetime objects to strings for JSON serialization
            serializable_results: Dict[str, Any] = dict(results.copy())

            # Convert trades
            for trade in serializable_results["trades"]:
                trade["entry_time"] = trade["entry_time"].isoformat()
                trade["exit_time"] = trade["exit_time"].isoformat()

            # Convert equity curve
            for point in serializable_results["equity_curve"]:
                point["timestamp"] = point["timestamp"].isoformat()

            with open(output_path, "w", encoding="utf-8") as f:
                try:
                    json.dump(serializable_results, f, indent=2)
                except IOError as e:
                    logger.error("Error while maintaining results: %s", e)
                    raise

            logger.info("Backtest results saved to %s", output_path)
            print(f"\nBacktest results saved to {output_path}")

    except KeyboardInterrupt:
        logger.info("Backtest stopped by user")
    except (ValueError, IOError, RuntimeError) as e:
        logger.exception("An error occurred: %s", e)
    finally:
        logger.info("Backtest runner completed")


if __name__ == "__main__":
    main()
