from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any

from dacite import Config as DaciteConfig
from dacite import from_dict

# todo: load this from a default renkon.toml
DEFAULTS: dict[str, dict[str, Any]] = {
    "repository": {
        "path": Path(".renkon"),
    },
    "server": {
        "hostname": IPv4Address("127.0.0.1"),
        "port": 1410,  # stroke counts of 蓮根 (renkon)
    },
}


@dataclass(frozen=True, kw_only=True, slots=True)
class RepositoryConfig:
    """
    Renkon repository configuration class.
    """

    path: Path = field(default=DEFAULTS["repository"]["path"])


@dataclass(frozen=True, kw_only=True, slots=True)
class ServerConfig:
    """
    Renkon server configuration class.
    """

    hostname: IPv4Address = field(default=DEFAULTS["server"]["hostname"])
    port: int = field(default=DEFAULTS["server"]["port"])


@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    """
    Renkon configuration class.
    """

    repository: RepositoryConfig = field(default_factory=RepositoryConfig)
    server: ServerConfig = field(default_factory=ServerConfig)


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

    conf = from_dict(data_class=Config, data=conf_data, config=DaciteConfig(cast=[Path, IPv4Address]))

    if update_global:
        global config  # noqa: PLW0603
        config = conf

    return conf


# Global configuration. Should not change after the first load,
# except for testing-specific purposes, or for CLI overrides.
config = load_config()
