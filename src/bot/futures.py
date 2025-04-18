#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Binance Futures Coin-M trading functionality.

This module provides functionality for trading on Binance Futures Coin-M markets
using the binance-futures-connector package.
"""

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd
# from binance_futures_connector.cm_futures import CMFutures
from binance.cm_futures import CMFutures  # type: ignore

from src.bot.indicators import QQEIndicator
from src.bot.utils import calculate_position_size
from src.config import (
    BINANCE_API_KEY,
    BINANCE_API_SECRET,
    BINANCE_BASE_URL,
    MAX_POSITION_SIZE,
    QQE_FAST_PERIOD,
    QQE_RSI_PERIOD,
    QQE_SLOW_PERIOD,
    QQE_SMOOTHING_PERIOD,
)
from src.logger import get_logger


class CoinMFuturesClient:
    """Client for Binance Futures Coin-M trading.

    This class provides methods for interacting with the Binance Futures Coin-M API,
    including fetching market data, placing orders, and managing positions.
    """

    def __init__(
            self,
            api_key: Optional[str] = None,
            api_secret: Optional[str] = None,
            base_url: Optional[str] = None,
    ) -> None:
        """Initialize the Coin-M Futures client.

        Args:
            api_key (str, optional): Binance API key. Defaults to None.
            api_secret (str, optional): Binance API secret. Defaults to None.
            base_url (str, optional): Binance API base URL. Defaults to None.
        """
        self.logger = get_logger("coin_m_futures")

        # Initialize client
        if api_key and api_secret:
            self.client = CMFutures(key=api_key, secret=api_secret, base_url=base_url)
            self.logger.info(
                "Initialized Binance Coin-M Futures client with API key authentication"
            )
        else:
            self.client = CMFutures()
            self.logger.info("Initialized Binance Coin-M Futures client in public mode")

    def fetch_historical_data(self, symbol: str, interval: str, limit: int = 500) -> pd.DataFrame:
        """Fetch historical klines data from Binance Futures Coin-M.

        Args:
            symbol (str): Trading pair symbol (e.g., BTCUSD_PERP)
            interval (str): Timeframe interval (e.g., 15m, 1h)
            limit (int, optional): Number of candles to fetch. Defaults to 500.

        Returns:
            pandas.DataFrame: DataFrame with historical data.
        """
        self.logger.info(f"Fetching historical data for {symbol} on {interval} timeframe")

        try:
            # Fetch klines data
            klines = self.client.klines(symbol=symbol, interval=interval, limit=limit)

            # Convert to DataFrame
            df = pd.DataFrame(
                klines,
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

        except Exception as e:
            self.logger.error(f"Error fetching historical data: {e}")
            raise

    def get_account_info(self) -> Dict[str, Any]:
        """Get account information including balances and positions.

        Returns:
            dict: Account information
        """
        try:
            return self.client.account()
        except Exception as e:
            self.logger.error(f"Error getting account information: {e}")
            raise

    def get_position_info(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get position information for a specific symbol or all positions.

        Args:
            symbol (str, optional): Trading pair symbol. Defaults to None (all positions).

        Returns:
            list: Position information
        """
        try:
            return self.client.get_position_risk(symbol=symbol)
        except Exception as e:
            self.logger.error(f"Error getting position information: {e}")
            raise

    def place_market_order(
            self, symbol: str, side: str, quantity: float, reduce_only: bool = False
    ) -> Dict[str, Any]:
        """Place a market order on Binance Futures Coin-M.

        Args:
            symbol (str): Trading pair symbol (e.g., BTCUSD_PERP)
            side (str): Order side (BUY or SELL)
            quantity (float): Order quantity
            reduce_only (bool, optional): Whether the order is reduce-only. Defaults to False.

        Returns:
            dict: Order response
        """
        try:
            return self.client.new_order(
                symbol=symbol,
                side=side,
                type="MARKET",
                quantity=quantity,
                reduceOnly=reduce_only,
            )
        except Exception as e:
            self.logger.error(f"Error placing market order: {e}")
            raise

    def place_limit_order(
            self,
            symbol: str,
            side: str,
            quantity: float,
            price: float,
            time_in_force: str = "GTC",
            reduce_only: bool = False,
    ) -> Dict[str, Any]:
        """Place a limit order on Binance Futures Coin-M.

        Args:
            symbol (str): Trading pair symbol (e.g., BTCUSD_PERP)
            side (str): Order side (BUY or SELL)
            quantity (float): Order quantity
            price (float): Order price
            time_in_force (str, optional): Time in force. Defaults to "GTC".
            reduce_only (bool, optional): Whether the order is reduce-only. Defaults to False.

        Returns:
            dict: Order response
        """
        try:
            return self.client.new_order(
                symbol=symbol,
                side=side,
                type="LIMIT",
                quantity=quantity,
                price=price,
                timeInForce=time_in_force,
                reduceOnly=reduce_only,
            )
        except Exception as e:
            self.logger.error(f"Error placing limit order: {e}")
            raise

    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """Cancel an order on Binance Futures Coin-M.

        Args:
            symbol (str): Trading pair symbol
            order_id (int): Order ID

        Returns:
            dict: Cancel response
        """
        try:
            return self.client.cancel_order(symbol=symbol, orderId=order_id)
        except Exception as e:
            self.logger.error(f"Error canceling order: {e}")
            raise

    def get_exchange_info(self) -> Dict[str, Any]:
        """Get exchange information including trading pairs and rules.

        Returns:
            dict: Exchange information
        """
        try:
            return self.client.exchange_info()
        except Exception as e:
            self.logger.error(f"Error getting exchange information: {e}")
            raise


class CoinMFuturesBot:
    """Trading bot for Binance Futures Coin-M markets using QQE indicator.

    This class extends the functionality of the main TradingBot class to support
    trading on Binance Futures Coin-M markets.
    """

    def __init__(self, trading_pair: str, timeframe: str, mode: str) -> None:
        """Initialize the Coin-M Futures trading bot.

        Args:
            trading_pair (str): Trading pair symbol (e.g., BTCUSD_PERP)
            timeframe (str): Timeframe for analysis (e.g., 15m, 1h)
            mode (str): Trading mode (paper, live)
        """
        self.logger = get_logger("coin_m_futures_bot")
        self.trading_pair = trading_pair
        self.timeframe = timeframe
        self.mode = mode
        self.running = False
        self.positions: Dict[str, Dict[str, Any]] = {}

        # Initialize indicators
        self.qqe = QQEIndicator(
            rsi_period=QQE_RSI_PERIOD,
            smoothing_period=QQE_SMOOTHING_PERIOD,
            fast_period=QQE_FAST_PERIOD,
            slow_period=QQE_SLOW_PERIOD,
        )

        # Initialize Binance Futures client
        self._init_futures_client()

    def _init_futures_client(self) -> None:
        """Initialize Binance Futures Coin-M API client."""
        api_key = BINANCE_API_KEY
        api_secret = BINANCE_API_SECRET
        base_url = BINANCE_BASE_URL

        if self.mode == "live" and (not api_key or not api_secret):
            self.logger.error("API key and secret are required for live trading")
            raise ValueError("API key and secret are required for live trading")

        # Initialize client
        self.client = CoinMFuturesClient(api_key=api_key, api_secret=api_secret, base_url=base_url)

    def fetch_historical_data(self, limit: int = 500) -> pd.DataFrame:
        """Fetch historical klines data from Binance Futures Coin-M.

        Args:
            limit (int, optional): Number of candles to fetch. Defaults to 500.

        Returns:
            pandas.DataFrame: DataFrame with historical data.
        """
        return self.client.fetch_historical_data(
            symbol=self.trading_pair, interval=self.timeframe, limit=limit
        )

    def analyze_market(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market data and generate trading signals.

        Args:
            data (pandas.DataFrame): Market data

        Returns:
            dict: Analysis results and trading signals
        """
        self.logger.info("Analyzing market data")

        # Apply QQE indicator
        qqe_data = self.qqe.calculate(data)

        # Get the latest values
        latest = qqe_data.iloc[-1]
        previous = qqe_data.iloc[-2] if len(qqe_data) > 1 else None

        # Generate signals
        signal = None
        if previous is not None:
            # QQE crossing above the zero line (bullish)
            if previous["qqe_value"] < 0 < latest["qqe_value"]:
                signal = "buy"
            # QQE crossing below the zero line (bearish)
            elif previous["qqe_value"] > 0 > latest["qqe_value"]:
                signal = "sell"

        return {
            "timestamp": latest.name,
            "close": data["close"].iloc[-1],
            "qqe_value": latest["qqe_value"],
            "qqe_trend": "bullish" if latest["qqe_value"] > 0 else "bearish",
            "signal": signal,
        }

    def execute_trade(self, signal: str, price: float) -> Dict[str, Any]:
        """Execute a trade based on the signal.

        Args:
            signal (str): Trading signal (buy, sell)
            price (float): Current price

        Returns:
            dict: Trade execution details
        """
        if self.mode == "paper":
            return self._paper_trade(signal, price)
        elif self.mode == "live":
            return self._live_trade(signal, price)
        else:
            self.logger.error(f"Unknown trading mode: {self.mode}")
            raise ValueError(f"Unknown trading mode: {self.mode}")

    def _paper_trade(self, signal: str, price: float) -> Dict[str, Any]:
        """Execute a paper trade.

        Args:
            signal (str): Trading signal (buy, sell)
            price (float): Current price

        Returns:
            dict: Paper trade details
        """
        self.logger.info(f"Paper trading: {signal} at price {price}")

        # Get account balance (in paper trading, we can simulate this)
        simulated_balance = 1000.0  # Simulated balance

        # Calculate position size
        position_size = calculate_position_size(
            balance=simulated_balance,
            price=price,
            risk_percent=MAX_POSITION_SIZE,
        )

        # Update positions dictionary
        if signal == "buy" and self.trading_pair not in self.positions:
            self.positions[self.trading_pair] = {
                "entry_price": price,
                "size": position_size,
                "entry_time": datetime.now().isoformat(),
            }
            self.logger.info(
                f"Opened paper position: {position_size} {self.trading_pair} at {price}"
            )
        elif signal == "sell" and self.trading_pair in self.positions:
            entry = self.positions[self.trading_pair]
            profit_loss = (price - entry["entry_price"]) * entry["size"]
            profit_loss_percent = (price - entry["entry_price"]) / entry["entry_price"] * 100

            self.logger.info(
                f"Closed paper position: {entry['size']} {self.trading_pair} at {price}. "
                f"P/L: {profit_loss:.2f} ({profit_loss_percent:.2f}%)"
            )
            del self.positions[self.trading_pair]

        return {
            "mode": "paper",
            "signal": signal,
            "price": price,
            "position_size": position_size if signal == "buy" else 0,
            "timestamp": datetime.now().isoformat(),
        }

    def _live_trade(self, signal: str, price: float) -> Dict[str, Any]:
        """Execute a live trade on Binance Futures Coin-M.

        Args:
            signal (str): Trading signal (buy, sell)
            price (float): Current price

        Returns:
            dict: Live trade details
        """
        self.logger.info(f"Live trading: {signal} signal at price {price}")

        try:
            # Get account information
            account_info = self.client.get_account_info()
            available_balance = float(account_info["availableBalance"])

            # Get current position
            positions = self.client.get_position_info(symbol=self.trading_pair)
            current_position = next(
                (p for p in positions if p["symbol"] == self.trading_pair), None
            )

            # Calculate position size
            position_size = calculate_position_size(
                balance=available_balance,
                price=price,
                risk_percent=MAX_POSITION_SIZE,
            )

            # Execute trade
            if signal == "buy":
                # Check if we already have a short position
                if current_position and float(current_position["positionAmt"]) < 0:
                    # Close existing short position
                    order = self.client.place_market_order(
                        symbol=self.trading_pair,
                        side="BUY",
                        quantity=abs(float(current_position["positionAmt"])),
                        reduce_only=True,
                    )
                    self.logger.info(f"Closed short position: {order}")

                # Open new long position
                order = self.client.place_market_order(
                    symbol=self.trading_pair, side="BUY", quantity=position_size
                )
                self.logger.info(f"Opened long position: {order}")

                return {
                    "mode": "live",
                    "signal": signal,
                    "price": price,
                    "position_size": position_size,
                    "order_id": order["orderId"],
                    "timestamp": datetime.now().isoformat(),
                }

            elif signal == "sell":
                # Check if we already have a long position
                if current_position and float(current_position["positionAmt"]) > 0:
                    # Close existing long position
                    order = self.client.place_market_order(
                        symbol=self.trading_pair,
                        side="SELL",
                        quantity=float(current_position["positionAmt"]),
                        reduce_only=True,
                    )
                    self.logger.info(f"Closed long position: {order}")

                # Open new short position
                order = self.client.place_market_order(
                    symbol=self.trading_pair, side="SELL", quantity=position_size
                )
                self.logger.info(f"Opened short position: {order}")

                return {
                    "mode": "live",
                    "signal": signal,
                    "price": price,
                    "position_size": position_size,
                    "order_id": order["orderId"],
                    "timestamp": datetime.now().isoformat(),
                }

            else:
                self.logger.warning(f"Unknown signal: {signal}")
                return {
                    "mode": "live",
                    "signal": signal,
                    "price": price,
                    "position_size": 0,
                    "error": "Unknown signal",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            self.logger.error(f"Error executing live trade: {e}")
            return {
                "mode": "live",
                "signal": signal,
                "price": price,
                "position_size": 0,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def run(self) -> None:
        """Run the trading bot."""
        self.logger.info(f"Starting Coin-M Futures trading bot in {self.mode} mode")
        self.running = True

        try:
            while self.running:
                # Fetch latest market data
                data = self.fetch_historical_data()

                # Analyze market data
                analysis = self.analyze_market(data)
                self.logger.info(
                    f"Market analysis: Price={analysis['close']}, QQE={analysis['qqe_value']:.2f}, "
                    f"Trend={analysis['qqe_trend']}"
                )

                # Execute trade if signal is present
                if analysis["signal"]:
                    trade_result = self.execute_trade(analysis["signal"], analysis["close"])
                    self.logger.info(f"Trade executed: {trade_result}")

                # Sleep to avoid API rate limits
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
        except Exception as e:
            self.logger.exception(f"An error occurred: {e}")
        finally:
            self.running = False
            self.logger.info("Bot shutdown complete")
