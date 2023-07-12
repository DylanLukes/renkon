from pathlib import Path

import pytest
from pyarrow import csv
from pyarrow import fs as pa_fs

from renkon.config import Config, load_config
from renkon.repo import Storage
from renkon.repo.registry import Registry, SQLiteRegistry
from renkon.repo.repository import Repository
from renkon.repo.storage import FileSystemStorage

TESTS_DIR = Path(__file__).parent

SEMICOLON_WITH_TYPE_ROW = {
    "parse_options": csv.ParseOptions(delimiter=";"),
    "read_options": csv.ReadOptions(skip_rows_after_names=1),
}

DEFAULT = {
    "parse_options": csv.ParseOptions(),
    "read_options": csv.ReadOptions(),
}

"""
List of sample datasets. Each key corresponds to a CSV file in the
`data` directory. Each contains the parse and read options needed
to read the file.
"""
SAMPLES = {
    "cars": SEMICOLON_WITH_TYPE_ROW,
    "cereals": SEMICOLON_WITH_TYPE_ROW,
    "cereals-corrupt": SEMICOLON_WITH_TYPE_ROW,
    "factbook": SEMICOLON_WITH_TYPE_ROW,
    "films": SEMICOLON_WITH_TYPE_ROW,
    "gini": DEFAULT,
    "smallwikipedia": SEMICOLON_WITH_TYPE_ROW,
}


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
    for name, options in SAMPLES.items():
        data = csv.read_csv(TESTS_DIR / "samples" / f"{name}.csv", **options)
        repo.put(name, data)
    return repo
