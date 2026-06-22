"""Advanced logging configuration using Loguru.

This module sets up application-wide logging with file rotation,
console output, and structured formatting.
"""

import sys
from pathlib import Path

from loguru import logger

from app.config import settings


class InterceptHandler:
    """Intercept standard logging and redirect to Loguru."""

    def emit(self, record) -> None:
        """Emit a log record to Loguru."""
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == __file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure application-wide logging.

    Sets up Loguru with:
    - Console output with colors
    - File output with rotation
    - Different formats for dev/prod
    """
    logger.remove()

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.logging.level,
        colorize=True,
        backtrace=True,
        diagnose=settings.is_development(),
    )

    log_path = Path(settings.logging.file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        str(log_path),
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
        level=settings.logging.level,
        rotation=(
            lambda _, __: Path(settings.logging.file).stat().st_size
            > settings.logging.max_bytes
        ),
        retention=settings.logging.backup_count,
        compression="zip",
        backtrace=True,
        diagnose=settings.is_development(),
        enqueue=True,
    )

    logger.add(
        "logs/errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}",
        level="ERROR",
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,
    )

    logger.info(
        f"Logging configured | Level: {settings.logging.level} | "
        f"Environment: {settings.app.environment}"
    )


__all__ = ["logger", "setup_logging"]