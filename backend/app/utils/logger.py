"""Centralized application logger with rotating file and console handlers."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config.settings import get_settings


def setup_logger(name: str = "student_analytics") -> logging.Logger:
    """Configure and return an application logger with rotating file and console handlers."""
    settings = get_settings()
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Rotating File Handler (10MB max, 5 backups)
    try:
        log_file_path = Path(settings.LOG_FILE)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            filename=str(log_file_path),
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        console_handler.setLevel(level)
        logger.warning(f"Could not initialize file log handler: {e}")

    logger.propagate = False
    return logger


# Default logger instance
logger = setup_logger()
