from importlib import resources
from pathlib import Path

import polars as pl
import pytest
from loguru import logger
from polars import DataFrame

from renkon.core.repo._repo import Repository
from renkon.core.repo.registry import Registry, SQLiteRegistry
from renkon.core.repo.storage import FileSystemStorage, Storage
from renkon.settings import Settings

TESTS_DIR = Path(__file__).parent
FIXTURES_DIR = TESTS_DIR / "fixtures"


@pytest.fixture(autouse=True, scope="session")
def reset_loguru() -> None:
    logger.remove()


@pytest.fixture
def working_dir(tmp_path: Path) -> Path:
    return tmp_path


@pytest.fixture(autouse=True)
def setup_test_dir(working_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Copy the settings to the working directory specified in the settings.
    settings_src = resources.files() / "renkon.tests.toml"
    settings_dst = working_dir / "renkon.toml"
    settings_dst.write_text(settings_src.read_text())

    # Switch to the working directory.
    monkeypatch.chdir(working_dir)


@pytest.fixture
def settings() -> Settings:
    return Settings()


@pytest.fixture
def registry(settings: Settings) -> Registry:
    path = settings.data_dir / "registry.db"
    return SQLiteRegistry(path)


@pytest.fixture
def storage(settings: Settings) -> Storage:
    root = settings.data_dir / "data"
    root.mkdir(parents=True, exist_ok=True)
    return FileSystemStorage(root)


@pytest.fixture
def repo(registry: Registry, storage: Storage) -> Repository:
    return Repository(registry=registry, storage=storage)


@pytest.fixture
def cereals_df() -> DataFrame:
    """
    Cereal nutrition dataset from https://www.kaggle.com/crawford/80-cereals
    """
    # Load cereal data from the data directory.
    path = FIXTURES_DIR / "data" / "cereals.csv"
    return pl.read_csv(
        path,
        separator=";",
        skip_rows_after_header=1,
    )
