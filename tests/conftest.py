from pathlib import Path

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
