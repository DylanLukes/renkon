from pathlib import Path, PurePath

import pyarrow as pa
import pytest

from renkon.repo import Storage

TABLE = pa.Table.from_pydict(
    mapping={"a": [1, 2, 3, 4, 5], "b": ["a", "b", "c", "d", "e"], "c": [True, False, True, False, True]}
)


def test_write_read_delete_parquet(storage: Storage) -> None:
    path = PurePath("foo/bar.parquet")

    storage.write(path, TABLE)
    assert storage.exists(path)

    table = storage.read(path)
    assert table is not None
    assert table.num_rows == 5
    assert table.num_columns == 3
    assert table.column_names == ["a", "b", "c"]
    assert table.column("a").to_pylist() == [1, 2, 3, 4, 5]
    assert table.column("b").to_pylist() == ["a", "b", "c", "d", "e"]
    assert table.column("c").to_pylist() == [True, False, True, False, True]

    storage.delete(path)
    assert not storage.exists(path)


def test_write_read_delete_arrow(storage: Storage) -> None:
    path = PurePath("foo/bar.parquet")

    storage.write(path, TABLE)
    assert storage.exists(path)

    table = storage.read(path)
    assert table is not None
    assert table.num_rows == 5
    assert table.num_columns == 3
    assert table.column_names == ["a", "b", "c"]
    assert table.column("a").to_pylist() == [1, 2, 3, 4, 5]
    assert table.column("b").to_pylist() == ["a", "b", "c", "d", "e"]
    assert table.column("c").to_pylist() == [True, False, True, False, True]

    storage.delete(path)
    assert not storage.exists(path)


def test_info_parquet(storage: Storage) -> None:
    path = PurePath("foo/bar.parquet")

    storage.write(path, TABLE)
    assert storage.exists(path)

    info = storage.info(path)
    assert info is not None
    assert info.path == path
    assert info.filetype == "parquet"
    assert info.schema.names == ["a", "b", "c"]
    assert info.rows == TABLE.num_rows
    assert info.size == (Path.cwd() / "data" / path).stat().st_size

    storage.delete(path)
    assert not storage.exists(path)


def test_info_arrow(storage: Storage) -> None:
    path = PurePath("foo/bar.arrow")

    storage.write(path, TABLE)
    assert storage.exists(path)

    info = storage.info(path)
    assert info is not None
    assert info.schema.names == ["a", "b", "c"]
    assert info.rows == TABLE.num_rows
    assert info.size == TABLE.nbytes

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
        storage.info(path)
