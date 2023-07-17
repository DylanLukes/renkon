from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path, PurePath
from sqlite3 import Connection as SQLiteConnection
from typing import Literal, Protocol, TypeAlias

from renkon.repo.info import SupportsRowFactory, TableDBTuple, TableInfo, TableStat
from renkon.repo.queries import queries
from renkon.util.common import serialize_schema

RegistryLookupKey: TypeAlias = Literal["name", "path"]
RegistrySearchKey: TypeAlias = Literal["name", "path"]


class Registry(Protocol):  # pragma: no cover
    def register(self, name: str, path: PurePath, table_info: TableStat) -> None:
        ...

    def unregister(self, name: str) -> None:
        ...

    def list_all(self) -> list[TableInfo]:
        ...

    def lookup(self, key: str, *, by: RegistryLookupKey) -> TableInfo | None:
        ...

    def search(self, query: str = "*", *, by: RegistrySearchKey) -> list[TableInfo]:
        ...


class SQLiteRegistry(Registry):
    """
    Handles all things related to metadata, composed by Repo.
    You should generally not need to interact with this class directly.
    """

    db_path: Path | Literal[":memory:"]

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._create_tables()

    @contextmanager
    def _connect(self, *, row_type: type[SupportsRowFactory] | None = None) -> Generator[SQLiteConnection, None, None]:
        """
        Get a connection to the metadata repository. This must be used in each method
        to avoid persisting a connection and risk it being used by multiple threads.

        :param row_type: a type which provides a row_factory method to set on the connection.
        """
        try:
            # note: using a connection object as a context manager implies
            # that commit will be called if no exception is raised, and rollback
            # otherwise.
            with sqlite3.connect(self.db_path) as conn:
                if row_type is not None:
                    conn.row_factory = row_type.row_factory
                yield conn
        finally:
            conn.close()

    def _create_tables(self) -> None:
        """
        Create tables in the metadata repository.
        """
        with self._connect() as conn:
            queries.create_tables(conn)

    def register(self, name: str, path: PurePath, table_info: TableStat) -> None:
        """
        Register a table.
        """
        with self._connect() as conn:
            queries.register_table(
                conn,
                path=str(path),
                name=name,
                filetype=table_info.filetype,
                schema=serialize_schema(table_info.schema),
                rows=table_info.rows,
                size=table_info.size,
            )

    def unregister(self, name: str) -> None:
        """
        Unregister a table.
        """
        with self._connect() as conn:
            queries.unregister_table(conn, name=name)

    def list_all(self) -> list[TableInfo]:
        """
        List all tables.
        """
        with self._connect(row_type=TableDBTuple) as conn:
            row_tuples = queries.list_tables(conn)
            return [TableInfo.from_tuple(row_tuple) for row_tuple in row_tuples]

    def lookup(self, key: str, *, by: RegistryLookupKey) -> TableInfo | None:
        row_tuple = None

        with self._connect(row_type=TableDBTuple) as conn:
            match by:
                case "name":
                    # Prefer parquet to arrow if both exist.
                    row_tuple = queries.get_table(conn, name=key, filetype="parquet")
                    row_tuple = row_tuple or queries.get_table(conn, name=key, filetype="arrow")
                case "path":
                    # The string path stored in the database is native (e.g. on Win: "foo/bar" -> "foo\\bar").
                    native_path = str(Path(key))
                    row_tuple = queries.get_table_by_path(conn, path=native_path)

        if row_tuple is None:
            return None

        return TableInfo.from_tuple(row_tuple)

    def search(self, query: str = "*", *, by: RegistrySearchKey) -> list[TableInfo]:
        row_tuples: list[TableDBTuple] = []
        with self._connect(row_type=TableDBTuple) as conn:
            match by:
                case "name":
                    # Prefer parquet to arrow if both exist
                    row_tuples = queries.search_tables_by_name(conn, name=query)
                case "path":
                    row_tuples = queries.search_tables_by_path(conn, path=query)

        return [TableInfo.from_tuple(values) for values in row_tuples]
