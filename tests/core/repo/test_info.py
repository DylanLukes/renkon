from pathlib import PurePath

import pytest

from renkon.core.repo.registry.base import FileType
from renkon.core.repo.registry.sqlite import TableRow
from renkon.core.repo.schema import to_arrow_schema_bytes
from renkon.core.repo.storage.base import Storage


def test_from_tuple_valid_filetype() -> None:
    """
    Test that a valid filetype is accepted.
    """
    file_types: list[FileType] = ["parquet", "arrow"]

    for file_type in file_types:
        TableRow(
            path="foo",
            name="bar",
            filetype=file_type,
            schema=to_arrow_schema_bytes({}),
            rows=0,
            size=0,
        ).to_entry()


def test_from_tuple_invalid_filetype() -> None:
    """
    Test that an invalid filetype raises an exception.
    """
    with pytest.raises(ValueError):
        TableRow(
            path="foo",
            name="bar",
            filetype="invalid",  # type: ignore[arg-type]
            schema=b"",
            rows=0,
            size=0,
        ).to_entry()


def test_from_stat() -> None:
    stat = Storage.Stat(path=PurePath("foo"), filetype="parquet", schema={}, rows=0, size=0)
    info = stat.to_entry(name="bar")

    assert info.name == "bar"
    assert info.path == PurePath("foo")
    assert info.filetype == "parquet"
    assert info.schema == {}
    assert info.rows == 0
    assert info.size == 0
