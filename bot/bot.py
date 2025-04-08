#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Core Trading Bot implementation.

This module contains the main TradingBot class that handles
connection to Binance API, market data processing, and trade execution.
"""

import os
import time
from datetime import datetime

import pandas as pd
from binance.spot import Spot
from dotenv_vault import load_dotenv

import config
from bot.indicators import QQEIndicator
from bot.logger import get_logger
from bot.utils import calculate_position_size

# Load environment variables
load_dotenv()


class TradingBot:
    """Trading bot for Binance using QQE indicator."""

    def __init__(self, trading_pair, timeframe, mode):
        """Initialize the trading bot.

        Args:
            trading_pair (str): Trading pair symbol (e.g., BTCUSDT)
            timeframe (str): Timeframe for analysis (e.g., 15m, 1h)
            mode (str): Trading mode (backtest, paper, live)
        """
        self.logger = get_logger()
        self.trading_pair = trading_pair
        self.timeframe = timeframe
        self.mode = mode
        self.running = False
        self.positions = {}

        # Initialize indicators
        self.qqe = QQEIndicator(
            rsi_period=config.QQE_RSI_PERIOD,
            smoothing_period=config.QQE_SMOOTHING_PERIOD,
            fast_period=config.QQE_FAST_PERIOD,
            slow_period=config.QQE_SLOW_PERIOD,
        )

        # Initialize Binance client
        self._init_binance_client()

    def _init_binance_client(self):
        """Initialize Binance API client."""
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")
        base_url = os.getenv("BINANCE_BASE_URL")


        if self.mode == config.MODE_LIVE and (not api_key or not api_secret):
            self.logger.error("API key and secret are required for live trading")
            raise ValueError("API key and secret are required for live trading")

        # Initialize client with or without authentication based on mode
        if self.mode == config.MODE_BACKTEST or (not api_key or not api_secret):
            self.client = Spot()
            self.logger.info("Initialized Binance client in public mode")
        else:
            self.client = Spot(api_key=api_key, api_secret=api_secret, base_url=base_url)
            self.logger.info("Initialized Binance client with API key authentication")

    def fetch_historical_data(self, limit=500):
        """Fetch historical klines data from Binance.

        Args:
            limit (int, optional): Number of candles to fetch. Defaults to 500.

        Returns:
            pandas.DataFrame: DataFrame with historical data.
        """
        self.logger.info(f"Fetching historical data for {self.trading_pair} on {self.timeframe} timeframe")
        
        try:
            # Convert timeframe to interval format expected by Binance API
            interval = self.timeframe
            
            # Fetch klines data
            klines = self.client.klines( symbol=self.trading_pair, interval=interval, limit=limit)
            
            # Convert to DataFrame
            df = pd.DataFrame(
                klines,
                columns=[
                    "timestamp", "open", "high", "low", "close", "volume",
                    "close_time", "quote_asset_volume", "number_of_trades",
                    "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
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

    def analyze_market(self, data):
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
            if previous["qqe_value"] < 0 and latest["qqe_value"] > 0:
                signal = "buy"
            # QQE crossing below the zero line (bearish)
            elif previous["qqe_value"] > 0 and latest["qqe_value"] < 0:
                signal = "sell"
        
        return {
            "timestamp": latest.name,
            "close": data["close"].iloc[-1],
            "qqe_value": latest["qqe_value"],
            "qqe_trend": "bullish" if latest["qqe_value"] > 0 else "bearish",
            "signal": signal,
        }

    def execute_trade(self, signal, price):
        """Execute a trade based on the signal.

        Args:
            signal (str): Trading signal (buy, sell)
            price (float): Current price

        Returns:
            dict: Trade execution details
        """
        if self.mode == config.MODE_BACKTEST:
            return self._simulate_trade(signal, price)
        elif self.mode == config.MODE_PAPER:
            return self._paper_trade(signal, price)
        elif self.mode == config.MODE_LIVE:
            return self._live_trade(signal, price)
        else:
            self.logger.error(f"Unknown trading mode: {self.mode}")
            raise ValueError(f"Unknown trading mode: {self.mode}")

    def _simulate_trade(self, signal, price):
        """Simulate a trade for backtesting.

        Args:
            signal (str): Trading signal (buy, sell)
            price (float): Current price

        Returns:
            dict: Trade simulation details
        """
        self.logger.info(f"Simulating {signal} trade at price {price}")
        
        # Implement backtesting logic here
        position_size = calculate_position_size(
            balance=1000.0,  # Simulated balance
            price=price,
            risk_percent=config.MAX_POSITION_SIZE,
        )
        
        return {
            "mode": "backtest",
            "signal": signal,
            "price": price,
            "position_size": position_size,
            "timestamp": datetime.now().isoformat(),
        }

    def _paper_trade(self, signal, price):
        """Execute a paper trade.

        Args:
            signal (str): Trading signal (buy, sell)
            price (float): Current price

        Returns:
            dict: Paper trade details
        """
        self.logger.info(f"Paper trading: {signal} at price {price}")
        
        # Get account balance (in paper trading, we can simulate this)
        simulated_balance = 1000.0  # Simulated balance in USDT
        
        # Calculate position size
        position_size = calculate_position_size(
            balance=simulated_balance,
            price=price,
            risk_percent=config.MAX_POSITION_SIZE,
        )
        
        # Update positions dictionary
        if signal == "buy" and self.trading_pair not in self.positions:
            self.positions[self.trading_pair] = {
                "entry_price": price,
                "size": position_size,
                "entry_time": datetime.now().isoformat(),
            }
            self.logger.info(f"Opened paper position: {position_size} {self.trading_pair} at {price}")
        elif signal == "sell" and self.trading_pair in self.positions:
            entry = self.positions[self.trading_pair]
            profit_loss = (price - entry["entry_price"]) * entry["size"]
            profit_loss_percent = (price - entry["entry_price"]) / entry["entry_price"] * 100
            
            self.logger.info(
                f"Closed paper position: {entry['size']} {self.trading_pair} at {price}. "
                f"P/L: {profit_loss:.2f} USDT ({profit_loss_percent:.2f}%)"
            )
            del self.positions[self.trading_pair]
        
        return {
            "mode": "paper",
            "signal": signal,
            "price": price,
            "position_size": position_size if signal == "buy" else 0,
            "timestamp": datetime.now().isoformat(),
        }

    def _live_trade(self, signal, price):
        """Execute a live trade on Binance.

        Args:
            signal (str): Trading signal (buy, sell)
            price (float): Current price

        Returns:
            dict: Live trade details
        """
        self.logger.info(f"Live trading: {signal} signal at price {price}")
        
        try:
            # Get account balance
            account_info = self.client.account()
            balances = {asset["asset"]: float(asset["free"]) for asset in account_info["balances"]}
            
            # Extract base and quote currencies correctly
            # Handle variable length trading pairs (e.g., BTCUSDT, ETHUSD, DOGEUSDT)
            for base in ["USDT", "BUSD", "BTC", "ETH"]:
                if self.trading_pair.endswith(base):
                    base_currency = base
                    quote_currency = self.trading_pair[:-len(base)]
                    break
            else:
                # Default fallback if no known base currency is found
                base_currency = self.trading_pair[-4:]
                quote_currency = self.trading_pair[:-4]
            
            base_balance = balances.get(base_currency, 0)
            quote_balance = balances.get(quote_currency, 0)
            
            # Calculate position size
            position_size = calculate_position_size(
                balance=base_balance,
                price=price,
                risk_percent=config.MAX_POSITION_SIZE,
            )
            
            # Execute trade
            if signal == "buy" and base_balance > 0:
                # Place market buy order
                order = self.client.new_order(
                    symbol=self.trading_pair,
                    side="BUY",
                    type="MARKET",
                    quoteOrderQty=position_size * price,  # Amount in base currency
                )
                self.logger.info(f"Placed buy order: {order}")
                return {
                    "mode": "live",
                    "signal": signal,
                    "price": price,
                    "position_size": position_size,
                    "order_id": order["orderId"],
                    "timestamp": datetime.now().isoformat(),
                }
            elif signal == "sell" and quote_balance > 0:
                # Place market sell order
                order = self.client.new_order(
                    symbol=self.trading_pair,
                    side="SELL",
                    type="MARKET",
                    quantity=quote_balance,  # Sell all available quote currency
                )
                self.logger.info(f"Placed sell order: {order}")
                return {
                    "mode": "live",
                    "signal": signal,
                    "price": price,
                    "position_size": quote_balance,
                    "order_id": order["orderId"],
                    "timestamp": datetime.now().isoformat(),
                }
            else:
                self.logger.warning(
                    f"Cannot execute {signal} trade: insufficient balance. "
                    f"Base balance: {base_balance}, Quote balance: {quote_balance}"
                )
                return {
                    "mode": "live",
                    "signal": signal,
                    "price": price,
                    "position_size": 0,
                    "error": "Insufficient balance",
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

    def run(self):
        """Run the trading bot."""
        self.logger.info(f"Starting trading bot in {self.mode} mode")
        self.running = True
        
        try:
            while self.running:
                # Fetch latest market data
                data = self.fetch_historical_data()
                
                # Analyze market data
                analysis = self.analyze_market(data)
                self.logger.info(
                    f"Market analysis: Price={analysis['close']}, "
                    f"QQE={analysis['qqe_value']:.2f}, Trend={analysis['qqe_trend']}"
                )
                
                # Execute trade if signal is present
                if analysis["signal"]:
                    trade_result = self.execute_trade(analysis["signal"], analysis["close"])
                    self.logger.info(f"Trade executed: {trade_result}")
                
                # Sleep until next candle
                if self.mode != config.MODE_BACKTEST:
                    self.logger.info("Waiting for next candle...")
                    # Calculate sleep time based on timeframe
                    sleep_time = self._get_sleep_time()
                    time.sleep(sleep_time)
                else:
                    # In backtest mode, we process all data at once
                    self.running = False
                    
        except KeyboardInterrupt:
            self.logger.info("Bot stopped by user")
            self.running = False
        except Exception as e:
            self.logger.exception(f"An error occurred: {e}")
            self.running = False

    def _get_sleep_time(self):
        """Calculate sleep time based on timeframe.
        
        Returns:
            int: Sleep time in seconds
        """
        # Map timeframes to seconds
        timeframe_seconds = {
            "1m": 60,
            "3m": 180,
            "5m": 300,
            "15m": 900,
            "30m": 1800,
            "1h": 3600,
            "2h": 7200,
            "4h": 14400,
            "6h": 21600,
            "8h": 28800,
            "12h": 43200,
            "1d": 86400,
            "3d": 259200,
            "1w": 604800,
        }
        
        # Get seconds for the current timeframe, default to 60 seconds if not found
        seconds = timeframe_seconds.get(self.timeframe, 60)
        
        # Return sleep time (slightly less than the full interval to ensure we don't miss candles)
        return max(30, seconds - 10)
    
    def stop(self):
        """Stop the trading bot."""
        self.logger.info("Stopping trading bot")
        self.running = False