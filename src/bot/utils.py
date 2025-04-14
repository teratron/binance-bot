#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Utility functions for the Binance Trading Bot.

This module provides helper functions for various tasks such as
position sizing, risk management, and data processing.
"""

import math
from datetime import datetime, timedelta

from src.logger import get_logger


def calculate_position_size(balance: float, price: float, risk_percent: float) -> float:
    """Calculate position size based on account balance and risk percentage.

    Args:
        balance (float): Account balance in base currency
        price (float): Current price of the asset
        risk_percent (float): Risk percentage as a decimal (e.g., 0.01 for 1%)

    Returns:
        float: Position size in quote currency
    """
    logger = get_logger()
    logger.debug(
        "Calculating position size: balance=%s, price=%s, risk=%s", balance, price, risk_percent
    )

    # Calculate the amount of base currency to risk
    risk_amount = balance * risk_percent

    # Calculate position size in quote currency
    position_size = risk_amount / price

    # Round down to 6 decimal places (common precision for crypto)
    position_size = math.floor(position_size * 1e6) / 1e6

    logger.debug("Calculated position size: %s", position_size)
    return position_size


def calculate_stop_loss(entry_price: float, side: str, stop_loss_percent: float) -> float:
    """Calculate stop loss price based on entry price and percentage.

    Args:
        entry_price (float): Entry price of the position
        side (str): Position side ('buy' or 'sell')
        stop_loss_percent (float): Stop loss percentage as a decimal

    Returns:
        float: Stop loss price
    """
    logger = get_logger()

    if side.lower() == "buy":
        stop_loss = entry_price * (1 - stop_loss_percent)
    else:  # sell
        stop_loss = entry_price * (1 + stop_loss_percent)

    logger.debug("Calculated stop loss: entry=%s, side=%s, stop=%s", entry_price, side, stop_loss)
    return stop_loss


def calculate_take_profit(entry_price: float, side: str, take_profit_percent: float) -> float:
    """Calculate take profit price based on entry price and percentage.

    Args:
        entry_price (float): Entry price of the position
        side (str): Position side ('buy' or 'sell')
        take_profit_percent (float): Take profit percentage as a decimal

    Returns:
        float: Take profit price
    """
    logger = get_logger()

    if side.lower() == "buy":
        take_profit = entry_price * (1 + take_profit_percent)
    else:  # sell
        take_profit = entry_price * (1 - take_profit_percent)

    logger.debug("Calculated take profit: entry=%s, side=%s, tp=%s", entry_price, side, take_profit)
    return take_profit


def format_number(number: float, precision: int = 8) -> float:
    """Format a number with specified precision.

    Args:
        number (float): Number to format
        precision (int, optional): Decimal precision. Defaults to 8.

    Returns:
        float: Formatted number
    """
    factor = 10 ** precision
    return math.floor(number * factor) / factor


def get_timeframe_delta(timeframe: str) -> timedelta:
    """Convert timeframe string to timedelta object.

    Args:
        timeframe (str): Timeframe string (e.g., '1m', '1h', '1d')

    Returns:
        timedelta: Equivalent timedelta object
    """
    unit = timeframe[-1]
    value = int(timeframe[:-1])

    if unit == "m":
        return timedelta(minutes=value)
    elif unit == "h":
        return timedelta(hours=value)
    elif unit == "d":
        return timedelta(days=value)
    elif unit == "w":
        return timedelta(weeks=value)
    else:
        raise ValueError(f"Unknown timeframe unit: {unit}")


def get_next_candle_time(timeframe: str) -> datetime:
    """Calculate the timestamp of the next candle based on the timeframe.

    Args:
        timeframe (str): Timeframe string (e.g., '1m', '1h', '1d')

    Returns:
        datetime: Timestamp of the next candle
    """
    now = datetime.now()
    _delta = get_timeframe_delta(timeframe)

    if timeframe.endswith("m"):
        # For minute timeframes
        minutes = int(timeframe[:-1])
        next_minute = ((now.minute // minutes) + 1) * minutes
        next_time = now.replace(minute=next_minute % 60, second=0, microsecond=0)
        if next_minute >= 60:
            next_time = next_time + timedelta(hours=next_minute // 60)
    elif timeframe.endswith("h"):
        # For hour timeframes
        hours = int(timeframe[:-1])
        next_hour = ((now.hour // hours) + 1) * hours
        next_time = now.replace(hour=next_hour % 24, minute=0, second=0, microsecond=0)
        if next_hour >= 24:
            next_time = next_time + timedelta(days=next_hour // 24)
    elif timeframe.endswith("d"):
        # For day timeframes
        next_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    return next_time


def calculate_sleep_time(timeframe: str) -> float:
    """Calculate sleep time until the next candle.

    Args:
        timeframe (str): Timeframe string (e.g., '1m', '1h', '1d')

    Returns:
        float: Sleep time in seconds
    """
    next_candle = get_next_candle_time(timeframe)
    now = datetime.now()
    sleep_seconds = (next_candle - now).total_seconds()

    # Add a small buffer to ensure we're past the candle close
    sleep_seconds += 1

    # Ensure we don't have a negative sleep time
    return max(1, sleep_seconds)
