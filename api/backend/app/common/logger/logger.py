import sys

from loguru import logger

from app.config import settings


def configure_logging() -> None:
    logger.remove()

    logger.add(
        sys.stderr,
        level="DEBUG" if settings.DEBUG else "INFO",
        enqueue=True,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
    )


def get_logger():
    return logger