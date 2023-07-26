from pathlib import Path
from typing import cast

import polars as pl
import pyarrow as pa
import pyarrow.csv
import pytest
from loguru import logger
from pyarrow import fs as pa_fs

from renkon.config import Config, load_config
from renkon.repo import Storage
from renkon.repo.registry import Registry, SQLiteRegistry
from renkon.repo.repository import Repository
from renkon.repo.storage import FileSystemStorage

TESTS_DIR = Path(__file__).parent


@pytest.fixture(autouse=True, scope="session")
def reset_loguru() -> None:
    logger.remove()


@pytest.fixture(autouse=True)
def change_test_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def config(tmp_path: Path) -> Config:
    return load_config(repository={"path": tmp_path})


@pytest.fixture
def registry(config: Config) -> Registry:
    path = config.repository.path / "metadata.db"
    return SQLiteRegistry(path)


@pytest.fixture
def storage(config: Config) -> Storage:
    path = config.repository.path / "data"
    path.mkdir(parents=True, exist_ok=True)
    local_fs = pa_fs.LocalFileSystem(use_mmap=True)
    storage_fs = pa_fs.SubTreeFileSystem(str(path), local_fs)
    return FileSystemStorage(storage_fs)


@pytest.fixture
def repo(registry: Registry, storage: Storage) -> Repository:
    repo = Repository(registry=registry, storage=storage)
    return repo


@pytest.fixture
def cereals_df() -> pl.DataFrame:
    """
    Cereal nutrition dataset from https://www.kaggle.com/crawford/80-cereals
    """
    # Load cereal data from the data directory.
    path = TESTS_DIR / "data" / "cereals.csv"
    table = pa.csv.read_csv(
        path,
        parse_options=pa.csv.ParseOptions(delimiter=";"),
        read_options=pa.csv.ReadOptions(skip_rows_after_names=1),
        convert_options=pa.csv.ConvertOptions(auto_dict_encode=True),
    )
    return cast(pl.DataFrame, pl.from_arrow(table))
