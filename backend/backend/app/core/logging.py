"""Structured logging configuration."""

import logging
import sys
from typing import Any


def setup_logging(debug: bool = False) -> None:
    """Configure application-wide logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger."""
    return logging.getLogger(name)


def log_action(logger: logging.Logger, action: str, **kwargs: Any) -> None:
    """Log an autonomous agent action with structured context."""
    context = " | ".join(f"{k}={v}" for k, v in kwargs.items())
    logger.info("AGENT_ACTION | %s | %s", action, context)
