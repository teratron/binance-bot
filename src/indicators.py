#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Technical indicators for the Binance Trading Bot.

This module contains implementations of various technical indicators,
including the QQE (Quantitative Qualitative Estimation) indicator.
"""

import numpy as np
from talib import EMA, RSI

from src.logger import get_logger


class QQEIndicator:
    """QQE (Quantitative Qualitative Estimation) indicator implementation.

    The QQE indicator is a modified RSI indicator that uses a smoothed ATR
    to create a dynamic, adaptive indicator that can identify trends and
    potential reversal points.
    """

    def __init__(self, rsi_period=14, smoothing_period=5, fast_period=2.618, slow_period=4.236):
        """Initialize QQE indicator.

        Args:
            rsi_period (int, optional): Period for RSI calculation. Defaults to 14.
            smoothing_period (int, optional): Period for smoothing. Defaults to 5.
            fast_period (float, optional): Fast period multiplier. Defaults to 2.618.
            slow_period (float, optional): Slow period multiplier. Defaults to 4.236.
        """
        self.rsi_period = rsi_period
        self.smoothing_period = smoothing_period
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.logger = get_logger()

    def calculate(self, data):
        """Calculate QQE indicator values.

        Args:
            data (pandas.DataFrame): Price data with 'close' column

        Returns:
            pandas.DataFrame: DataFrame with QQE indicator values
        """
        self.logger.info("Calculating QQE indicator values")

        # Make a copy of the data to avoid modifying the original
        df = data.copy()

        # Calculate RSI
        try:
            df["rsi"] = RSI(df["close"], timeperiod=self.rsi_period)
        except Exception as e:
            self.logger.error("Error calculating RSI: %s", e)
            raise

        # Calculate smoothed RSI
        df["smoothed_rsi"] = EMA(df["rsi"], timeperiod=self.smoothing_period)

        # Calculate True Range of RSI
        df["rsi_tr"] = abs(df["smoothed_rsi"].shift(1) - df["smoothed_rsi"])

        # Calculate ATR of RSI
        df["rsi_atr"] = EMA(df["rsi_tr"], timeperiod=self.smoothing_period)

        # Calculate fast and slow QQE bands
        df["fast_band"] = df["rsi_atr"] * self.fast_period
        df["slow_band"] = df["rsi_atr"] * self.slow_period

        # Initialize QQE values
        df["qqe_value"] = np.nan
        df["long_band"] = np.nan
        df["short_band"] = np.nan

        # Calculate QQE values using a rolling window approach
        for i in range(self.rsi_period + self.smoothing_period, len(df)):
            if i == self.rsi_period + self.smoothing_period:
                # Initialize first value
                df.loc[df.index[i], "qqe_value"] = df.loc[df.index[i], "smoothed_rsi"]
                df.loc[df.index[i], "long_band"] = (
                    df.loc[df.index[i], "smoothed_rsi"] - df.loc[df.index[i], "slow_band"]
                )
                df.loc[df.index[i], "short_band"] = (
                    df.loc[df.index[i], "smoothed_rsi"] + df.loc[df.index[i], "slow_band"]
                )
            else:
                # Get previous values
                prev_qqe = df.loc[df.index[i - 1], "qqe_value"]
                prev_long = df.loc[df.index[i - 1], "long_band"]
                prev_short = df.loc[df.index[i - 1], "short_band"]
                curr_rsi = df.loc[df.index[i], "smoothed_rsi"]
                _fast_band = df.loc[df.index[i], "fast_band"]
                slow_band = df.loc[df.index[i], "slow_band"]

                # Calculate new long and short bands
                if prev_qqe > prev_long and curr_rsi > prev_long:
                    new_long = max(prev_long, curr_rsi - slow_band)
                else:
                    new_long = curr_rsi - slow_band

                if prev_qqe < prev_short and curr_rsi < prev_short:
                    new_short = min(prev_short, curr_rsi + slow_band)
                else:
                    new_short = curr_rsi + slow_band

                # Calculate new QQE value
                if prev_qqe > prev_short and curr_rsi > new_short:
                    new_qqe = new_short
                elif prev_qqe < prev_long and curr_rsi < new_long:
                    new_qqe = new_long
                else:
                    # Trend continuation
                    if curr_rsi > prev_qqe and curr_rsi > new_long:
                        new_qqe = new_long
                    elif curr_rsi < prev_qqe and curr_rsi < new_short:
                        new_qqe = new_short
                    else:
                        new_qqe = prev_qqe

                # Store new values
                df.loc[df.index[i], "qqe_value"] = new_qqe
                df.loc[df.index[i], "long_band"] = new_long
                df.loc[df.index[i], "short_band"] = new_short

        # Calculate QQE zero line crossings
        df["qqe_zero_cross"] = 0
        df.loc[(df["qqe_value"] > 50) & (df["qqe_value"].shift(1) <= 50), "qqe_zero_cross"] = (
            1  # Bullish cross
        )
        df.loc[
            (df["qqe_value"] < 50) & (df["qqe_value"].shift(1) >= 50), "qqe_zero_cross"
        ] = -1  # Bearish cross

        # Normalize QQE value to oscillate around zero
        df["qqe_value"] = df["qqe_value"] - 50

        self.logger.info("QQE indicator calculation completed")
        return df


class EMACrossover:
    """EMA Crossover indicator implementation."""

    def __init__(self, fast_period=20, slow_period=50):
        """Initialize EMA Crossover indicator.

        Args:
            fast_period (int, optional): Fast EMA period. Defaults to 20.
            slow_period (int, optional): Slow EMA period. Defaults to 50.
        """
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.logger = get_logger()

    def calculate(self, data):
        """Calculate EMA Crossover indicator values.

        Args:
            data (pandas.DataFrame): Price data with 'close' column

        Returns:
            pandas.DataFrame: DataFrame with EMA Crossover indicator values
        """
        self.logger.info("Calculating EMA Crossover indicator values")

        # Make a copy of the data to avoid modifying the original
        df = data.copy()

        # Calculate EMAs
        df["fast_ema"] = EMA(df["close"], timeperiod=self.fast_period)
        df["slow_ema"] = EMA(df["close"], timeperiod=self.slow_period)

        # Calculate crossover signals
        df["ema_cross"] = 0
        df.loc[
            (df["fast_ema"] > df["slow_ema"])
            & (df["fast_ema"].shift(1) <= df["slow_ema"].shift(1)),
            "ema_cross",
        ] = 1  # Bullish cross
        df.loc[
            (df["fast_ema"] < df["slow_ema"])
            & (df["fast_ema"].shift(1) >= df["slow_ema"].shift(1)),
            "ema_cross",
        ] = -1  # Bearish cross

        self.logger.info("EMA Crossover calculation completed")
        return df


class VolumeProfile:
    """Volume Profile indicator implementation."""

    def __init__(self, num_bins=20, lookback_period=100):
        """Initialize Volume Profile indicator.

        Args:
            num_bins (int, optional): Number of price bins. Defaults to 20.
            lookback_period (int, optional): Lookback period. Defaults to 100.
        """
        self.num_bins = num_bins
        self.lookback_period = lookback_period
        self.logger = get_logger()

    def calculate(self, data):
        """Calculate Volume Profile indicator values.

        Args:
            data (pandas.DataFrame): Price data with 'high', 'low', 'close', and 'volume' columns

        Returns:
            dict: Dictionary with Volume Profile indicator values
        """
        self.logger.info("Calculating Volume Profile indicator values")

        # Make a copy of the data to avoid modifying the original
        df = data.copy().tail(self.lookback_period)

        # Calculate price range
        price_min = df["low"].min()
        price_max = df["high"].max()
        price_range = price_max - price_min
        bin_size = price_range / self.num_bins

        # Create price bins
        bins = [price_min + i * bin_size for i in range(self.num_bins + 1)]

        # Calculate volume profile
        volume_profile = {}
        for i in range(self.num_bins):
            bin_low = bins[i]
            bin_high = bins[i + 1]
            bin_mid = (bin_low + bin_high) / 2

            # Calculate volume in this price bin
            mask = (df["low"] <= bin_high) & (df["high"] >= bin_low)
            bin_volume = df.loc[mask, "volume"].sum()

            volume_profile[bin_mid] = bin_volume

        # Find point of control (price level with highest volume)
        poc_price = max(volume_profile, key=volume_profile.get)
        poc_volume = volume_profile[poc_price]

        self.logger.info("Volume Profile calculation completed")
        return {
            "volume_profile": volume_profile,
            "poc_price": poc_price,
            "poc_volume": poc_volume,
            "price_bins": bins,
        }
