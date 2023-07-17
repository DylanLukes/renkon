from pathlib import PurePath

import pyarrow as pa
import pytest

from renkon.repo.info import FileType, TableDBTuple, TableInfo, TableStat
from renkon.util.common import serialize_schema


def test_from_tuple_valid_filetype() -> None:
    """
    Test that a valid filetype is accepted.
    """
    file_types: list[FileType] = ["parquet", "arrow"]

    for file_type in file_types:
        TableInfo.from_tuple(
            TableDBTuple(
                path="foo",
                name="bar",
                filetype=file_type,
                schema=serialize_schema(pa.schema([])),
                rows=0,
                size=0,
            )
        )


def test_from_tuple_invalid_filetype() -> None:
    """
    Test that an invalid filetype raises an exception.
    """
    with pytest.raises(ValueError):
        TableInfo.from_tuple(
            TableDBTuple(
                path="foo",
                name="bar",
                filetype="invalid",  # type: ignore[arg-type]
                schema=b"",
                rows=0,
                size=0,
            )
        )


def test_from_stat() -> None:
    stat = TableStat(path=PurePath("foo"), filetype="parquet", schema=pa.schema([]), rows=0, size=0)
    info = TableInfo.from_stat(name="bar", stat=stat)

    assert info.name == "bar"
    assert info.path == PurePath("foo")
    assert info.filetype == "parquet"
    assert info.schema == pa.schema([])
    assert info.rows == 0
    assert info.size == 0
