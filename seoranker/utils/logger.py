import logging
from pathlib import Path
from seoranker.config.settings import LOG_LEVEL, LOG_FORMAT

def setup_logger(name: str) -> logging.Logger:
    """Set up logger with proper formatting"""
    logger = logging.getLogger(name)
    
    # Only add handlers if none exist
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)  # Only INFO and above to console
        console_format = logging.Formatter('%(message)s')  # Simplified console format
        console_handler.setFormatter(console_format)
        
        # File handler for debug logs
        file_handler = logging.FileHandler('logs/debug.log')
        file_handler.setLevel(logging.DEBUG)
        file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_format)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger 