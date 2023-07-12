from __future__ import annotations

import atexit
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from sqlite3 import Connection as SQLiteConnection
from typing import Protocol

import pyarrow as pa

from renkon.repo.queries import TableTuple, queries
from renkon.repo.storage import StoredTableInfo
from renkon.util.common import deserialize_schema, serialize_schema


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


class Registry(Protocol):
    def register(self, name: str, path: str, table_info: StoredTableInfo) -> None:
        ...

    def unregister(self, name: str) -> None:
        ...

    def get_table_by_name(self, name: str) -> RegisteredTableInfo | None:
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

    def get_table_by_name(self, name: str) -> RegisteredTableInfo | None:
        """
        Get a table by name.
        """
        if (values := queries.get_table_by_name(self.conn, name=name)) is None:
            return None
        return RegisteredTableInfo.from_values(values)
