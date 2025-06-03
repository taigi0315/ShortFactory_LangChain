"""
Logger configuration for the ShortFactory application.
"""

import os
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging(log_level=logging.INFO, log_dir="logs"):
    """
    Set up logging for the application.
    
    Args:
        log_level: Minimum log level to capture
        log_dir: Directory to store log files
    """
    # Create logs directory if it doesn't exist
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(log_level)
    
    # Create file handler for detailed logs
    detailed_log_path = os.path.join(log_dir, "shortfactory_detailed.log")
    detailed_file_handler = RotatingFileHandler(
        detailed_log_path, maxBytes=10*1024*1024, backupCount=5
    )
    detailed_file_handler.setFormatter(detailed_formatter)
    detailed_file_handler.setLevel(log_level)
    
    # Create file handler for errors only
    error_log_path = os.path.join(log_dir, "shortfactory_errors.log")
    error_file_handler = RotatingFileHandler(
        error_log_path, maxBytes=10*1024*1024, backupCount=5
    )
    error_file_handler.setFormatter(detailed_formatter)
    error_file_handler.setLevel(logging.ERROR)
    
    # Add all handlers to root logger
    root_logger.addHandler(console_handler)
    root_logger.addHandler(detailed_file_handler)
    root_logger.addHandler(error_file_handler)
    
    logging.info("Logging system initialized.")
