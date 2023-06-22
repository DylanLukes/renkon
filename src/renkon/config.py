from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Config:
    """
    Renkon configuration class.
    """

    # Location to store data on disk.
    store_dir: Path = Path.cwd() / ".renkon"

    # Prettify superscripts.
    pretty_superscripts: bool = True

    # Prettify subscripts.
    pretty_subscripts: bool = True

    # Pretty colors.
    pretty_colors: bool = True


@lru_cache(1)
def get_config(**overrides: Any) -> Config:
    """
    TODO: Load from TOML file .renkon/config.toml if it exists.

    Otherwise, return the (default) Renkon configuration.
    """

    return Config(**overrides)
