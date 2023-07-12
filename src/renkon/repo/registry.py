from __future__ import annotations

import atexit
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection as SQLiteConnection
from typing import Literal, Protocol, TypeAlias

import pyarrow as pa

from renkon.repo.queries import TableTuple, queries
from renkon.repo.storage import StoredTableInfo
from renkon.util.common import deserialize_schema, serialize_schema, unreachable


@dataclass(frozen=True, kw_only=True, slots=True)
class RegisteredTableInfo:
    name: str
    path: str
    schema: pa.Schema
    rows: int
    size: int

    @classmethod
    def from_values(cls, values: TableTuple) -> RegisteredTableInfo:
        _, name, path, schema, rows, size = values
        return cls(
            name=name,
            path=path,
            schema=deserialize_schema(schema),
            rows=rows,
            size=size,
        )


RegistryLookupKey: TypeAlias = Literal["name", "path"]


class Registry(Protocol):
    def register(self, name: str, path: str, table_info: StoredTableInfo) -> None:
        ...

    def unregister(self, name: str) -> None:
        ...

    def lookup(self, key: str, *, by: RegistryLookupKey) -> RegisteredTableInfo | None:
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

    def register(self, name: str, path: str, table_info: StoredTableInfo) -> None:
        """
        Register a table.
        """
        queries.register_table(
            self.conn,
            name=name,
            path=path,
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
                values = queries.get_table_by_name(self.conn, name=key)
            case "path":
                values = queries.get_table_by_path(self.conn, path=key)
            case _:
                unreachable()

        if values is None:
            return None

        return RegisteredTableInfo.from_values(values)
