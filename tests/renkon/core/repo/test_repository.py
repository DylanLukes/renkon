import pytest
from polars import DataFrame

from renkon.core.repo import Registry
from renkon.core.repo.repository import Repository

DATA = DataFrame({
    "a": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "b": ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    "c": [True, False, True, False, True, False, True, False, True, False],
})


def test_round_trip(repo: Repository) -> None:
    repo.put("foo/bar", DATA)
    assert repo.exists("foo/bar")
    data = repo.get("foo/bar")
    assert data is not None
    assert data.equals(DATA)


def test_put_bad_path(repo: Repository) -> None:
    with pytest.raises(ValueError, match="cannot have a suffix"):
        repo.put("foo/bar.parquet", DATA)


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


def test_get_nonexistent(repo: Repository) -> None:
    assert repo.get("foo/bar") is None


def test_get_info(repo: Repository) -> None:
    repo.put("foo/bar", DATA)
    info = repo.get_info("foo/bar")
    assert info is not None
    assert info.name == "foo/bar"
    assert info.filetype == "parquet"
    assert not info.schema.keys() - {"a", "b", "c"}


def test_list_info(repo: Repository) -> None:
    repo.put("foo/bar", DATA)
    repo.put("foo/baz", DATA)
    repo.put("foo/qux", DATA)
    info = repo.list_info()
    assert len(info) == 3
    assert info[0].name == "foo/bar"
    assert info[1].name == "foo/baz"
    assert info[2].name == "foo/qux"
