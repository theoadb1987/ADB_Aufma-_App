# utils/logger.py
"""
Logging utility functions for the application.
"""
import os
import sys
import logging
from datetime import datetime

# Path resolution
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """Create and configure a logger with the given name and level."""
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove any existing handlers to avoid duplicates
    if logger.handlers:
        for handler in logger.handlers:
            logger.removeHandler(handler)
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Set up file handler with daily rotating log files
    log_date = datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(logs_dir, f"aufmass_{log_date}.log")
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(level)
    
    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # Set formatters
    file_handler.setFormatter(file_formatter)
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def configure_global_logging(level: int = logging.INFO) -> None:
    """
    Configure global logging settings.
    
    Args:
        level: Logging level to set globally
    """
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Suppress noisy loggers
    logging.getLogger('PyQt6').setLevel(logging.WARNING)
