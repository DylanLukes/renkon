from pathlib import Path

import pytest

from renkon.config import Config
from renkon.store.store import Store
from tests.conftest import SAMPLES


def test_get_store(tmp_path: Path, config: Config, store: Store) -> None:
    assert store.root_dir == config.store.path.resolve() == tmp_path / ".renkon"


def test_get_sample_input_paths(store: Store) -> None:
    assert store.root_dir.exists()
    assert store.root_dir.is_dir()

    for name in SAMPLES:
        path = store.get_input_table_path(name)
        assert path is not None
        assert (store.root_dir / path).exists()
        assert (store.root_dir / path).is_file()


def test_get_sample_input_tables(store: Store) -> None:
    assert store.root_dir.exists()
    assert store.root_dir.is_dir()

    for name in SAMPLES:
        data = store.get_input_table(name)
        assert data is not None
        assert data.num_rows > 0
        assert data.num_columns > 0


def test_get_non_existent(store: Store) -> None:
    with pytest.raises(LookupError):
        store.get_input_table_path("non_existent")

    with pytest.raises(LookupError):
        store.get_input_table("non_existent")
