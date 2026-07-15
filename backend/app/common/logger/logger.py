import os
import sys

from loguru import logger

from app.config import settings


def configure_logging() -> None:
    logger.remove()

    # Disable enqueue in serverless environments (Vercel) where multiprocessing is limited
    is_serverless = os.environ.get("VERCEL") is not None

    logger.add(
        sys.stderr,
        level="DEBUG" if settings.DEBUG else "INFO",
        enqueue=not is_serverless,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG,
    )


def get_logger():
    return logger