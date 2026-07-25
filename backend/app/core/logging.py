import logging
import sys
import os
from logging.handlers import RotatingFileHandler
from app.config.settings import settings

def setup_logging() -> None:
    """
    Configure application logging to both console and file.
    Ensures logs are stored in the logs/ directory with a timestamped format.
    """
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file_path = os.path.join(log_dir, "agilegraph.log")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # File Handler
    file_handler = RotatingFileHandler(
        log_file_path, maxBytes=10485760, backupCount=5
    )
    file_handler.setFormatter(formatter)

    # Root Logger Configuration
    logger = logging.getLogger()
    logger.setLevel(settings.LOG_LEVEL.upper())
    
    # Remove existing handlers to prevent duplicate logs in some environments
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
