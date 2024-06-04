from __future__ import annotations

import tomllib
from importlib import resources
from pathlib import Path
from typing import cast

from pydantic import BaseModel, FilePath, field_validator
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, TomlConfigSettingsSource


class RepositorySettings(BaseModel):
    pass


class Settings(BaseSettings):
    data_dir: Path = Path(".renkon")

    model_config = SettingsConfigDict(
        env_prefix="renkon_",
        toml_file=[
            # TODO: https://github.com/pydantic/pydantic-settings/issues/299
            cast(Path, resources.files("renkon").joinpath("renkon.defaults.toml")),
            "renkon.toml",
        ],
    )

    @field_validator("data_dir")
    @classmethod
    def check_data_dir_not_existing_file(cls, data_dir: Path) -> Path:
        if data_dir.exists() and not data_dir.is_dir():
            msg = f"{data_dir} cannot be an existing file."
            raise ValueError(msg)

        return data_dir.resolve()

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        default_sources = super().settings_customise_sources(
            settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings
        )
        return *default_sources, TomlConfigSettingsSource(settings_cls)

    @classmethod
    def from_toml(cls, toml_file: FilePath) -> Settings:
        with toml_file.open("rb") as f:
            config_data = tomllib.load(f)
            return cls(**config_data)
