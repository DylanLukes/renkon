from __future__ import annotations

import atexit
import sqlite3
from dataclasses import dataclass
from pathlib import Path, PurePath
from sqlite3 import Connection as SQLiteConnection
from typing import Literal, Protocol, TypeAlias, cast

import pyarrow as pa

from renkon.repo.queries import TableTuple, queries
from renkon.repo.storage import StoredTableInfo
from renkon.util.common import deserialize_schema, serialize_schema, unreachable


@dataclass(frozen=True, kw_only=True, slots=True)
class RegisteredTableInfo:
    path: PurePath
    name: str
    filetype: Literal["parquet", "arrow"]
    schema: pa.Schema
    rows: int
    size: int

    @classmethod
    def from_values(cls, values: TableTuple) -> RegisteredTableInfo:
        path, name, filetype, schema, rows, size = values
        if filetype not in ("parquet", "arrow"):
            msg = f"Invalid filetype: {filetype}"
            raise ValueError(msg)
        return cls(
            name=name,
            path=PurePath(path),
            filetype=cast(Literal["parquet", "arrow"], filetype),  # todo: alias and use type guard instead
            schema=deserialize_schema(schema),
            rows=rows,
            size=size,
        )


RegistryLookupKey: TypeAlias = Literal["name", "path"]
RegistrySearchKey: TypeAlias = Literal["name", "path"]


class Registry(Protocol):
    def register(self, name: str, path: PurePath, table_info: StoredTableInfo) -> None:
        ...

    def unregister(self, name: str) -> None:
        ...

    def lookup(self, key: str, *, by: RegistryLookupKey) -> RegisteredTableInfo | None:
        ...

    def search(self, query: str = "*", *, by: RegistrySearchKey) -> list[RegisteredTableInfo]:
        ...


class SQLiteRegistry(Registry):
    """
    Handles all things related to metadata, composed by Repo.
    You should generally not need to interact with this class directly.
    """

    path: Path
    conn: SQLiteConnection

    def __init__(self, path: Path) -> None:
        self.conn = sqlite3.connect(path)
        atexit.register(self.conn.close)
        self._create_tables()

    def _create_tables(self, *, commit: bool = True) -> None:
        """
        Create tables in the metadata repository.
        """
        queries.create_tables(self.conn)
        if commit:
            self.conn.commit()

    def register(self, name: str, path: PurePath, table_info: StoredTableInfo) -> None:
        """
        Register a table.
        """
        queries.register_table(
            self.conn,
            path=str(path),
            name=name,
            filetype=table_info.filetype,
            schema=serialize_schema(table_info.schema),
            rows=table_info.rows,
            size=table_info.size,
        )
        self.conn.commit()

    def unregister(self, name: str) -> None:
        """
        Unregister a table.
        """
        queries.unregister_table(self.conn, name=name)

    def lookup(self, key: str, *, by: RegistryLookupKey) -> RegisteredTableInfo | None:
        values = None
        match by:
            case "name":
                # Prefer parquet to arrow if both exist
                values = queries.get_table(self.conn, name=key, filetype="parquet")
                values = values or queries.get_table(self.conn, name=key, filetype="arrow")
            case "path":
                values = queries.get_table_by_path(self.conn, path=key)
            case _:
                unreachable()

        if values is None:
            return None

        return RegisteredTableInfo.from_values(values)

    def search(self, query: str = "*", *, by: RegistrySearchKey) -> list[RegisteredTableInfo]:
        values_list: list[TableTuple] = []
        match by:
            case "name":
                # Prefer parquet to arrow if both exist
                values_list = queries.search_tables_by_name(self.conn, name=query)
            case "path":
                values_list = queries.search_tables_by_path(self.conn, path=query)

        return [RegisteredTableInfo.from_values(values) for values in values_list]
