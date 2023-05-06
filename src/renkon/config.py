from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from loguru import logger


@dataclass(frozen=True, slots=True)
class Config:
    """
    Renkon configuration class.
    """

    # Location to store data on disk.
    store_dir: Path = Path.cwd() / ".renkon"


@lru_cache(1)
def get_config(**overrides: Any) -> Config:
    """
    Return the (default) Renkon configuration.
    """

    return Config(**overrides)
