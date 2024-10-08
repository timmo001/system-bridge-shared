"""Logger."""

import contextlib
import logging
from logging.handlers import RotatingFileHandler
import os

from colorlog import ColoredFormatter

from .common import get_user_data_directory

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
FORMAT = "%(asctime)s %(levelname)s (%(threadName)s) [%(name)s] %(message)s"


def setup_logger(
    log_level: str,
    name: str,
) -> logging.Logger:
    """Set up logging."""

    logging.basicConfig(
        datefmt=DATE_FORMAT,
        format=FORMAT,
        level=log_level,
    )

    logging.getLogger().handlers[0].setFormatter(
        ColoredFormatter(
            f"%(log_color)s{FORMAT}%(reset)s",
            datefmt=DATE_FORMAT,
            reset=True,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red",
            },
        )
    )

    file_handler = RotatingFileHandler(
        os.path.join(get_user_data_directory(), f"{name}.log"),
        backupCount=1,
        maxBytes=1024 * 1024 * 10,  # 10MB
    )
    contextlib.suppress(PermissionError)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(FORMAT, datefmt=DATE_FORMAT))

    logger = logging.getLogger("")
    logger.addHandler(file_handler)
    logger.setLevel(log_level)

    return logger
