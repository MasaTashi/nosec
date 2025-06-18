"""
Logger Module

This module provides utilities for setting up logging for the application.
"""

import os
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional


def setup_logger(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_size: int = 10485760,  # 10 MB
    backup_count: int = 5,
    format_str: Optional[str] = None
) -> logging.Logger:
    """
    Set up the application logger.
    
    Args:
        level: Logging level
        log_file: Path to log file (optional)
        max_size: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        format_str: Log format string (optional)
        
    Returns:
        Configured logger
    """
    # Get root logger
    logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Set logging level
    logger.setLevel(level)
    
    # Create formatter
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(format_str)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Create file handler if log file is specified
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_size,
            backupCount=backup_count
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_log_level(level: int) -> None:
    """
    Set the log level for the root logger.
    
    Args:
        level: Logging level
    """
    logging.getLogger().setLevel(level)


def get_log_level_from_string(level_str: str) -> int:
    """
    Convert a string log level to a logging level constant.
    
    Args:
        level_str: String log level (e.g., 'INFO', 'DEBUG')
        
    Returns:
        Logging level constant
    """
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    return level_map.get(level_str.upper(), logging.INFO)