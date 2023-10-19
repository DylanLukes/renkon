from __future__ import annotations

import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from importlib import resources
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any

import dacite

_DEFAULT_CONF_DATA = tomllib.load(resources.files().joinpath("defaults.toml").open("rb"))


@dataclass(frozen=True, kw_only=True, slots=True)
class RepositoryConfig:
    """
    Configuration for Renkon's repository.
    """

    path: Path = field(default=_DEFAULT_CONF_DATA["repository"]["path"])


@dataclass(frozen=True, kw_only=True, slots=True)
class ServerConfig:
    """
    Configuration for Renkon when running as a server.
    """

    hostname: IPv4Address = field(default=_DEFAULT_CONF_DATA["server"]["hostname"])
    port: int = field(default=_DEFAULT_CONF_DATA["server"]["port"])


@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    """
    Renkon configuration class.
    """

    repository: RepositoryConfig = field(default_factory=RepositoryConfig)
    server: ServerConfig = field(default_factory=ServerConfig)

    @staticmethod
    def from_dict(data: Mapping[str, Any]) -> Config:
        return dacite.from_dict(data_class=Config, data=data, config=dacite.Config(cast=[Path, IPv4Address]))

    @staticmethod
    def load(**overrides: Any) -> Config:
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

        return Config.from_dict(conf_data)

    @staticmethod
    def defaults() -> Config:
        return Config.from_dict(_DEFAULT_CONF_DATA)
