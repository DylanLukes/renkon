import os
import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "| {process} "
    "| {module}"
    "| {level} "
    "| <level>{message}</level>",
)
