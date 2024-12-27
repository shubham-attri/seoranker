import logging
from seoranker.config.settings import LOG_LEVEL, LOG_FORMAT

def setup_logger(name):
    """Set up logger for the given module"""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Create console handler with formatting
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger 