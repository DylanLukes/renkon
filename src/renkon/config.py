from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dacite import Config as DaciteConfig
from dacite import from_dict


@dataclass(frozen=True, kw_only=True, slots=True)
class StoreConfig:
    """
    Renkon store configuration class.
    """

    path: Path = Path.cwd() / ".renkon"


@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    """
    Renkon configuration class.
    """

    store: StoreConfig = field(default_factory=StoreConfig)


def load_config(*, update_global: bool = False, **overrides: Any) -> Config:
    """
    Load the configuration from renkon.toml, and apply overrides.

    :param update_global: Whether to update the global configuration.
    :param overrides: Configuration overrides.
    :return: The configuration.
    """

    # If renkon.toml exists in the working directory, load it using pathlib.
    conf_data = {}
    if (p := Path.cwd() / "renkon.toml").exists():
        with p.open("rb") as f:
            conf_data = tomllib.load(f)

    # Apply overrides.
    conf_data.update(overrides)

    conf = from_dict(data_class=Config, data=conf_data, config=DaciteConfig(cast=[Path]))

    if update_global:
        global config  # noqa: PLW0603
        config = conf

    return conf


# Global configuration. Should not change after the first load,
# except for testing-specific purposes, or for CLI overrides.
config = load_config()
