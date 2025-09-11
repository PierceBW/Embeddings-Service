"""logging_config.py
Centralised logging configuration for the Risk Predictor service.
Call `setup_logging()` once at application start-up.
"""
from __future__ import annotations

import logging
from logging.config import dictConfig


def setup_logging(level: str = "INFO") -> None:
    """Configure root and module loggers.

    Parameters
    ----------
    level: str
        Root log level (e.g., "INFO", "DEBUG").
    """
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console": {
                    "()": "logging.Formatter",
                    "fmt": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": {
                "default": {
                    "level": level,
                    "formatter": "console",
                    "class": "logging.StreamHandler",
                }
            },
            "root": {"level": level, "handlers": ["default"]},
        }
    )