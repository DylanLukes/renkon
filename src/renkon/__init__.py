import sys

from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
    "| {process} "
    "| {module}"
    "| {level} "
    "| <level>{message}</level>",
)
