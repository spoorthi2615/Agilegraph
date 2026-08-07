import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict

from app.config.settings import settings

# Context variable to store the Correlation ID (X-Request-ID)
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class StructuredJsonFormatter(logging.Formatter):
    """
    Formatter that outputs JSON strings for production environments.
    Includes correlation IDs, timestamps, process IDs, and thread IDs.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.name,
            "process": record.process,
            "thread": record.thread,
            "request_id": request_id_ctx.get(),
            "environment": settings.ENVIRONMENT,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_record)


def setup_logging() -> None:
    """
    Initializes the centralized logging framework.
    Replaces basicConfig and intercepts uvicorn/fastapi loggers.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers to avoid duplicates
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)

    # Use JSON formatter in production/testing, standard formatter in dev (optional, but requested structured so we use JSON always)
    console_handler.setFormatter(StructuredJsonFormatter())

    root_logger.addHandler(console_handler)

    # Overwrite uvicorn loggers to use our formatter
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logger = logging.getLogger(logger_name)
        logger.handlers = [console_handler]
        logger.setLevel(log_level)
        logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """
    Returns a configured logger instance for the given module name.
    """
    return logging.getLogger(name)
