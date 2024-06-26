# SPDX-FileCopyrightText: 2024-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import inspect
import logging
import os
import sys

from loguru import logger


def configure_logging(
    intercept_loggers: list[str] | None = None,
):
    if intercept_loggers is None:
        intercept_loggers = ["uvicorn.asgi", "uvicorn.access", "uvicorn.error", "fastapi"]

    # Configure Loguru to handle standard logging messages.
    logger_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: >8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    logger.configure(
        handlers=[
            {
                "sink": sys.stderr,
                "level": os.environ.get("LOG_LEVEL", "INFO"),
                "format": logger_format,
                "colorize": True,
            }
        ]
    )

    # Intercept standard logging messages and redirect them to Loguru.
    intercept_handler = InterceptHandler()
    for intercept_logger in intercept_loggers:
        logging.getLogger(intercept_logger).handlers = [intercept_handler]
    #
    # logger.trace("Trace log")
    # logger.debug("Debug log")
    # logger.info("Info log")
    # logger.success("Success log")
    # logger.warning("Warning log")
    # logger.error("Error log")
    # logger.critical("Critical log")


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists.
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
