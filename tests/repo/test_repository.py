import pyarrow as pa
import pytest

from renkon.repo import Registry
from renkon.repo.repository import Repository

DATA = pa.Table.from_pydict(
    mapping={
        "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "b": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
        "c": [True, False, True, False, True, False, True, False, True, False],
    }
)


def test_round_trip(repo: Repository) -> None:
    repo.put("foo/bar", DATA)
    assert repo.exists("foo/bar")
    data = repo.get("foo/bar")
    assert data is not None
    assert data.num_rows == 10
    assert data.num_columns == 3
    assert data.column_names == ["a", "b", "c"]
    assert data.equals(DATA)


def test_put_for_storage_only(repo: Repository, registry: Registry) -> None:
    repo.put("foo/bar", DATA, for_storage=True, for_ipc=False)
    assert registry.lookup("foo/bar", by="name") is not None
    assert registry.lookup("foo/bar.parquet", by="path") is not None


def test_put_for_ipc_only(repo: Repository, registry: Registry) -> None:
    repo.put("foo/bar", DATA, for_ipc=True, for_storage=True)
    assert registry.lookup("foo/bar", by="name") is not None
    assert registry.lookup("foo/bar.arrow", by="path") is not None


def test_put_for_both(repo: Repository, registry: Registry) -> None:
    repo.put("foo/bar", DATA, for_ipc=True, for_storage=True)
    assert registry.lookup("foo/bar", by="name") is not None
    assert registry.lookup("foo/bar.arrow", by="path") is not None
    assert registry.lookup("foo/bar.parquet", by="path") is not None


def test_put_for_neither_fails(repo: Repository, registry: Registry) -> None:
    with pytest.raises(ValueError, match="Cannot store data for neither IPC nor storage."):
        repo.put("foo/bar", DATA, for_ipc=False, for_storage=False)
    assert registry.lookup("foo/bar", by="name") is None
    assert registry.lookup("foo/bar.parquet", by="path") is None
    assert registry.lookup("foo/bar.arrow", by="path") is None
