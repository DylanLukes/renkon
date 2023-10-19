from pathlib import Path, PurePath

import pytest
from polars import DataFrame

from renkon.core.repo import Storage

TABLE = DataFrame({"a": [1, 2, 3, 4, 5], "b": ["a", "b", "c", "d", "e"], "c": [True, False, True, False, True]})


def test_write_read_delete_parquet(storage: Storage) -> None:
    path = PurePath("foo/bar.parquet")

    storage.write(path, TABLE)
    assert storage.exists(path)

    table = storage.read(path)
    assert table is not None
    assert table.frame_equal(TABLE)

    storage.delete(path)
    assert not storage.exists(path)


def test_write_read_delete_arrow(storage: Storage) -> None:
    path = PurePath("foo/bar.arrow")

    storage.write(path, TABLE)
    assert storage.exists(path)

    table = storage.read(path)
    assert table is not None
    assert table.frame_equal(TABLE)

    storage.delete(path)
    assert not storage.exists(path)


def test_info_parquet(storage: Storage) -> None:
    path = PurePath("foo/bar.parquet")

    storage.write(path, TABLE)
    assert storage.exists(path)

    info = storage.stat(path)
    assert info is not None
    assert info.path == path
    assert info.filetype == "parquet"
    assert not info.schema.keys() - {"a", "b", "c"}
    assert info.rows == len(TABLE)
    assert info.size == (Path.cwd() / "data" / path).stat().st_size

    storage.delete(path)
    assert not storage.exists(path)


def test_info_arrow(storage: Storage) -> None:
    path = PurePath("foo/bar.arrow")

    storage.write(path, TABLE)
    assert storage.exists(path)

    info = storage.stat(path)
    assert info is not None
    assert not info.schema.keys() - {"a", "b", "c"}
    assert info.rows == len(TABLE)

    storage.delete(path)
    assert not storage.exists(path)


def test_unhandled_extension(storage: Storage) -> None:
    path = PurePath("foo/bar.csv")

    # Read
    with pytest.raises(ValueError, match="Unknown file extension: .csv"):
        storage.read(path)

    # Write
    with pytest.raises(ValueError, match="Unknown file extension: .csv"):
        storage.write(path, TABLE)

    # Info
    with pytest.raises(ValueError, match="Unknown file extension: .csv"):
        storage.stat(path)
