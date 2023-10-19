from pathlib import Path
from typing import cast

import polars as pl
import pyarrow.csv
import pytest
from loguru import logger
from polars import DataFrame
from pyarrow import fs as pa_fs

from renkon.config import Config
from renkon.core.repo import SQLiteRegistry, Storage
from renkon.core.repo.registry import Registry
from renkon.core.repo.repository import Repository
from renkon.core.repo.storage import FileSystemStorage

TESTS_DIR = Path(__file__).parent


@pytest.fixture(autouse=True, scope="session")
def reset_loguru() -> None:
    logger.remove()


@pytest.fixture(autouse=True)
def change_test_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def config(tmp_path: Path) -> Config:
    return Config.load(repository={"path": tmp_path})


@pytest.fixture
def registry(config: Config) -> Registry:
    path = config.repository.path / "registry.db"
    return SQLiteRegistry(path)


@pytest.fixture
def storage(config: Config) -> Storage:
    root = config.repository.path / "data"
    root.mkdir(parents=True, exist_ok=True)
    return FileSystemStorage(root)


@pytest.fixture
def repo(registry: Registry, storage: Storage) -> Repository:
    repo = Repository(registry=registry, storage=storage)
    return repo


@pytest.fixture
def cereals_df() -> DataFrame:
    """
    Cereal nutrition dataset from https://www.kaggle.com/crawford/80-cereals
    """
    # Load cereal data from the data directory.
    path = TESTS_DIR / "data" / "cereals.csv"
    table = pl.read_csv(
        path,
        separator=";",
        skip_rows_after_header=1,
    )
    return table
