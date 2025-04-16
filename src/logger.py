#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Logger module.

This module provides logging functionality for the trading bot,
including console and file logging with rotation.
"""
import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv_vault import load_dotenv

from src.config import (
    LOG_BACKUP_COUNT,
    LOG_FILE,
    LOG_FORMAT,
    LOG_LEVEL,
    LOG_MAX_SIZE,
)

# Load environment variables
load_dotenv()


def setup_logger(log_level: str | None = None) -> logging.Logger:
    """Set up and configure the logger.

    Args:
        log_level (str, optional): Logging level. Defaults to None.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Get log level from environment or config
    if log_level is None:
        log_level = os.getenv("LOG_LEVEL", LOG_LEVEL)

    # Create logs directory if it doesn't exist
    log_dir: Path = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure logger
    logger = logging.getLogger("binance_bot")
    logger.setLevel(getattr(logging, log_level))

    # Clear existing handlers to avoid duplicate logs
    if logger.handlers:
        logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT)

    # Create console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    # console_handler.close()

    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        log_dir / LOG_FILE,
        maxBytes=LOG_MAX_SIZE,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    #file_handler.close()

    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Get the logger instance.

    Args:
        name (str, optional): Name of the logger. Defaults to None.

    Returns:
        logging.Logger: Logger instance.
    """
    return logging.getLogger(name)
