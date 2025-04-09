#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Backtesting module for the Binance Trading Bot.

This module provides functionality for backtesting trading strategies
using historical data from Binance.
"""

from datetime import datetime

import config
import pandas as pd
from binance.spot import Spot

from ..logger import get_logger
from .indicators import QQEIndicator
from .utils import calculate_position_size


class Backtester:
    """Backtester for trading strategies."""

    def __init__(self, trading_pair, timeframe, start_date, end_date=None, initial_balance=1000.0):
        """Initialize the backtester.

        Args:
            trading_pair (str): Trading pair symbol (e.g., BTCUSDT)
            timeframe (str): Timeframe for analysis (e.g., 15m, 1h)
            start_date (str): Start date for backtesting (YYYY-MM-DD)
            end_date (str, optional): End date for backtesting (YYYY-MM-DD). Defaults to None (current date).
            initial_balance (float, optional): Initial balance for backtesting. Defaults to 1000.0.
        """
        self.logger = get_logger()
        self.trading_pair = trading_pair
        self.timeframe = timeframe
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") if end_date else datetime.now()
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = None
        self.trades = []
        self.equity_curve = []

        # Initialize client
        self.client = Spot()

        # Initialize indicators
        self.qqe = QQEIndicator(
            rsi_period=config.QQE_RSI_PERIOD,
            smoothing_period=config.QQE_SMOOTHING_PERIOD,
            fast_period=config.QQE_FAST_PERIOD,
            slow_period=config.QQE_SLOW_PERIOD,
        )

        self.logger.info(
            f"Initialized backtester for {trading_pair} on {timeframe} timeframe "
            f"from {start_date} to {end_date or 'now'}"
        )

    def fetch_historical_data(self):
        """Fetch historical klines data from Binance for the specified period.

        Returns:
            pandas.DataFrame: DataFrame with historical data.
        """
        self.logger.info(f"Fetching historical data for {self.trading_pair}")

        # Convert dates to milliseconds timestamp
        start_ts = int(self.start_date.timestamp() * 1000)
        end_ts = int(self.end_date.timestamp() * 1000)

        # Fetch data in chunks to handle API limitations
        all_klines = []
        current_ts = start_ts

        while current_ts < end_ts:
            try:
                # Fetch 1000 candles at a time (Binance limit)
                klines = self.client.klines(
                    symbol=self.trading_pair,
                    interval=self.timeframe,
                    startTime=current_ts,
                    limit=1000,
                )

                if not klines:
                    break

                all_klines.extend(klines)

                # Update current timestamp for next iteration
                current_ts = klines[-1][0] + 1

                self.logger.debug(
                    f"Fetched {len(klines)} candles from {datetime.fromtimestamp(klines[0][0] / 1000)}"
                )

            except Exception as e:
                self.logger.error(f"Error fetching historical data: {e}")
                break

        if not all_klines:
            self.logger.error("No historical data fetched")
            return pd.DataFrame()

        # Convert to DataFrame
        df = pd.DataFrame(
            all_klines,
            columns=[
                "timestamp",
                "open",
                "high",
                "low",
                "close",
                "volume",
                "close_time",
                "quote_asset_volume",
                "number_of_trades",
                "taker_buy_base_asset_volume",
                "taker_buy_quote_asset_volume",
                "ignore",
            ],
        )

        # Convert types
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col])

        self.logger.info(f"Fetched {len(df)} candles of historical data")
        return df

    def run_backtest(self, data=None):
        """Run backtest on historical data.

        Args:
            data (pandas.DataFrame, optional): Historical data. If None, data will be fetched.

        Returns:
            dict: Backtest results
        """
        self.logger.info("Starting backtest")

        # Fetch data if not provided
        if data is None:
            data = self.fetch_historical_data()

        if data.empty:
            self.logger.error("No data available for backtesting")
            return {"error": "No data available for backtesting"}

        # Apply QQE indicator
        data = self.qqe.calculate(data)

        # Reset backtest state
        self.balance = self.initial_balance
        self.position = None
        self.trades = []
        self.equity_curve = [{"timestamp": data["timestamp"].iloc[0], "equity": self.balance}]

        # Run backtest
        for i in range(1, len(data)):
            current = data.iloc[i]
            previous = data.iloc[i - 1]

            # Record equity at each candle
            equity = self.balance
            if self.position:
                # Add unrealized profit/loss if in a position
                if self.position["side"] == "buy":
                    equity += self.position["size"] * (
                        current["close"] - self.position["entry_price"]
                    )
                else:  # sell
                    equity += self.position["size"] * (
                        self.position["entry_price"] - current["close"]
                    )

            self.equity_curve.append({"timestamp": current["timestamp"], "equity": equity})

            # Check for signals
            signal = None

            # QQE crossing above the zero line (bullish)
            if previous["qqe_value"] < 0 < current["qqe_value"]:
                signal = "buy"
            # QQE crossing below the zero line (bearish)
            elif previous["qqe_value"] > 0 > current["qqe_value"]:
                signal = "sell"

            # Process signals
            if signal:
                if signal == "buy" and not self.position:
                    # Open long position
                    self._open_position("buy", current["close"], current["timestamp"])
                elif signal == "sell" and self.position and self.position["side"] == "buy":
                    # Close long position
                    self._close_position(current["close"], current["timestamp"])
                elif signal == "sell" and not self.position:
                    # Open short position (if allowed)
                    if config.ALLOW_SHORT_SELLING:
                        self._open_position("sell", current["close"], current["timestamp"])
                elif signal == "buy" and self.position and self.position["side"] == "sell":
                    # Close short position
                    self._close_position(current["close"], current["timestamp"])

        # Close any open position at the end of the backtest
        if self.position:
            self._close_position(data["close"].iloc[-1], data["timestamp"].iloc[-1])

        # Calculate backtest results
        results = self._calculate_results()
        self.logger.info(f"Backtest completed: {results['summary']}")

        return results

    def _open_position(self, side, price, timestamp):
        """Open a new position.

        Args:
            side (str): Position side (buy or sell)
            price (float): Entry price
            timestamp (datetime): Entry timestamp
        """
        # Calculate position size
        position_size = calculate_position_size(
            balance=self.balance,
            price=price,
            risk_percent=config.MAX_POSITION_SIZE,
        )

        # Record position
        self.position = {
            "side": side,
            "entry_price": price,
            "size": position_size,
            "entry_time": timestamp,
        }

        self.logger.debug(f"Opened {side} position: {position_size} at {price}")

    def _close_position(self, price, timestamp):
        """Close an open position.

        Args:
            price (float): Exit price
            timestamp (datetime): Exit timestamp
        """
        if not self.position:
            return

        # Calculate profit/loss
        if self.position["side"] == "buy":
            profit_loss = (price - self.position["entry_price"]) * self.position["size"]
        else:  # sell
            profit_loss = (self.position["entry_price"] - price) * self.position["size"]

        # Update balance
        self.balance += profit_loss

        # Record trade
        trade = {
            "side": self.position["side"],
            "entry_price": self.position["entry_price"],
            "exit_price": price,
            "size": self.position["size"],
            "entry_time": self.position["entry_time"],
            "exit_time": timestamp,
            "profit_loss": profit_loss,
            "profit_loss_percent": (
                profit_loss / (self.position["entry_price"] * self.position["size"])
            )
            * 100,
        }

        self.trades.append(trade)

        self.logger.debug(
            f"Closed {self.position['side']} position: {self.position['size']} at {price}. "
            f"P/L: {profit_loss:.2f} ({trade['profit_loss_percent']:.2f}%)"
        )

        # Reset position
        self.position = None

    def _calculate_results(self):
        """Calculate backtest results.

        Returns:
            dict: Backtest results
        """
        if not self.trades:
            return {
                "initial_balance": self.initial_balance,
                "final_balance": self.balance,
                "total_return": 0,
                "total_return_percent": 0,
                "num_trades": 0,
                "win_rate": 0,
                "profit_factor": 0,
                "max_drawdown": 0,
                "max_drawdown_percent": 0,
                "trades": [],
                "equity_curve": self.equity_curve,
                "summary": "No trades executed",
            }

        # Calculate performance metrics
        total_return = self.balance - self.initial_balance
        total_return_percent = (total_return / self.initial_balance) * 100

        winning_trades = [t for t in self.trades if t["profit_loss"] > 0]
        losing_trades = [t for t in self.trades if t["profit_loss"] <= 0]

        num_trades = len(self.trades)
        num_winning = len(winning_trades)
        win_rate = (num_winning / num_trades) * 100 if num_trades > 0 else 0

        total_profit = sum(t["profit_loss"] for t in winning_trades)
        total_loss = abs(sum(t["profit_loss"] for t in losing_trades))
        profit_factor = total_profit / total_loss if total_loss > 0 else float("inf")

        # Calculate max drawdown
        max_equity = self.initial_balance
        max_drawdown = 0
        max_drawdown_percent = 0

        for point in self.equity_curve:
            equity = point["equity"]
            max_equity = max(max_equity, equity)
            drawdown = max_equity - equity
            drawdown_percent = (drawdown / max_equity) * 100

            max_drawdown = max(max_drawdown, drawdown)
            max_drawdown_percent = max(max_drawdown_percent, drawdown_percent)

        # Create summary
        summary = (
            f"Total Return: {total_return:.2f} ({total_return_percent:.2f}%), "
            f"Trades: {num_trades}, Win Rate: {win_rate:.2f}%, "
            f"Profit Factor: {profit_factor:.2f}, Max Drawdown: {max_drawdown_percent:.2f}%"
        )

        return {
            "initial_balance": self.initial_balance,
            "final_balance": self.balance,
            "total_return": total_return,
            "total_return_percent": total_return_percent,
            "num_trades": num_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "max_drawdown": max_drawdown,
            "max_drawdown_percent": max_drawdown_percent,
            "trades": self.trades,
            "equity_curve": self.equity_curve,
            "summary": summary,
        }


def run_backtest(trading_pair, timeframe, start_date, end_date=None, initial_balance=1000.0):
    """Run a backtest with the specified parameters.

    Args:
        trading_pair (str): Trading pair symbol (e.g., BTCUSDT)
        timeframe (str): Timeframe for analysis (e.g., 15m, 1h)
        start_date (str): Start date for backtesting (YYYY-MM-DD)
        end_date (str, optional): End date for backtesting (YYYY-MM-DD). Defaults to None.
        initial_balance (float, optional): Initial balance for backtesting. Defaults to 1000.0.

    Returns:
        dict: Backtest results
    """
    backtester = Backtester(
        trading_pair=trading_pair,
        timeframe=timeframe,
        start_date=start_date,
        end_date=end_date,
        initial_balance=initial_balance,
    )

    return backtester.run_backtest()
