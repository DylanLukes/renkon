from __future__ import annotations

import sqlite3
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import PurePath
from typing import Any, Literal, NamedTuple, Protocol, TypeAlias, TypeGuard, TypeVar

import pyarrow as pa

from renkon.util.common import deserialize_schema

FileType: TypeAlias = Literal["parquet", "arrow"]


# Type guard for FileType
def is_valid_filetype(value: str) -> TypeGuard[FileType]:
    return value in ("parquet", "arrow")


_RowT = TypeVar("_RowT")
_TupleT = TypeVar("_TupleT", bound=tuple[Any, ...])
RowFactory: TypeAlias = Callable[[sqlite3.Cursor, _TupleT], _RowT]


_T = TypeVar("_T")


class SupportsRowFactory(Protocol):
    @classmethod
    def row_factory(cls: type[_T], cur: sqlite3.Cursor, row: tuple[Any, ...]) -> _T:
        ...


class TableDBTuple(NamedTuple):
    """
    Tuple type for a table record in the metadata registry (database).
    """

    path: str
    name: str
    filetype: FileType
    schema: bytes
    rows: int
    size: int

    @classmethod
    def row_factory(cls: type[TableDBTuple], _cur: sqlite3.Cursor, row: tuple[Any, ...]) -> TableDBTuple:
        return cls(*row)


"""
Tuple type for a table record in the metadata registry (database).
"""


@dataclass(frozen=True, kw_only=True, slots=True)
class TableInfo:
    """
    Information record for a table according to the metadata registry (database).
    """

    path: PurePath
    name: str
    filetype: FileType
    schema: pa.Schema
    rows: int
    size: int

    @classmethod
    def from_tuple(cls, values: TableDBTuple) -> TableInfo:
        """
        Convert a tuple of values from the database into a TableInfo object.
        """
        if not is_valid_filetype(values.filetype):
            msg = f"Invalid filetype: {values.filetype}"
            raise ValueError(msg)
        return cls(
            name=values.name,
            path=PurePath(values.path),
            filetype=values.filetype,
            schema=deserialize_schema(values.schema),
            rows=values.rows,
            size=values.size,
        )

    @classmethod
    def from_stat(cls, name: str, stat: TableStat) -> TableInfo:
        """
        Create a TableInfo object from a TableStat object and name.
        """
        return cls(
            name=name,
            path=stat.path,
            filetype=stat.filetype,
            schema=stat.schema,
            rows=stat.rows,
            size=stat.size,
        )


@dataclass(frozen=True, kw_only=True, slots=True)
class TableStat:
    """
    Information about a table in storage, produced by the storage backend
    from the underlying data.

    :field path: Logical path to the table in storage.
    :field filetype: Filetype of the table, either "parquet" or "arrow".
    :field schema: Schema of the table.
    :field rows: Number of rows in the table, or -1 if unknown.
    :field size: Size of the serialized table in bytes, or -1 if unknown.
    """

    path: PurePath
    filetype: FileType
    schema: pa.Schema
    rows: int = -1
    size: int = -1
