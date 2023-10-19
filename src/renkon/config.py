from __future__ import annotations

import tomllib
from dataclasses import dataclass
from ipaddress import IPv4Address
from pathlib import Path
from typing import Any

import dacite

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

# DEFAULT_CONFIG =


@dataclass(frozen=True, kw_only=True, slots=True)
class RepositoryConfig:
    """
    Configuration for Renkon's repository.
    """

    path: Path


@dataclass(frozen=True, kw_only=True, slots=True)
class ServerConfig:
    """
    Configuration for Renkon when running as a server.
    """

    hostname: IPv4Address
    port: int


@dataclass(frozen=True, kw_only=True, slots=True)
class Config:
    """
    Renkon configuration class.
    """

    repository: RepositoryConfig | None
    server: ServerConfig | None

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

        conf = dacite.from_dict(data_class=Config, data=conf_data, config=dacite.Config(cast=[Path, IPv4Address]))
        return conf
