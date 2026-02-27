import logging
import sys

from .config import settings


def setup_logging() -> None:
    """
    Configure application-wide logging.
    
    Uses a simple, readable format for development.
    Log level is controlled via the LOG_LEVEL env var.
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Format: timestamp - logger name - level - message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-25s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger("aviannet")
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Quiet noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a child logger under the 'aviannet' namespace."""
    return logging.getLogger(f"aviannet.{name}")
