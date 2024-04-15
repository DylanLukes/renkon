from __future__ import annotations

import sqlite3
from collections.abc import Callable, Generator
from contextlib import contextmanager
from pathlib import Path
from sqlite3 import Connection as SQLiteConnection
from typing import TYPE_CHECKING, Any, Literal, Protocol, Self

from renkon.core.repo.registry.base import Registry
from renkon.core.repo.registry.sqlite import TableRow
from renkon.core.repo.registry.sqlite.queries import queries
from renkon.core.repo.schema import to_arrow_schema_bytes

if TYPE_CHECKING:
    from renkon.core.repo.registry import LookupKey, SearchKey

type RowFactory[RowT, TupleT: tuple[Any, ...]] = Callable[[sqlite3.Cursor, TupleT], RowT]


class SupportsRowFactory(Protocol):
    @classmethod
    def row_factory(cls, cur: sqlite3.Cursor, row: tuple[Any, ...]) -> Self:
        ...


class SQLiteRegistry(Registry):
    """
    SQLite-based implementation of the table registry.
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
        conn = None
        try:
            # note: using a connection object as a context manager implies
            # that commit will be called if no exception is raised, and rollback
            # otherwise.
            with sqlite3.connect(self.db_path) as conn:
                if row_type is not None:
                    conn.row_factory = row_type.row_factory
                yield conn
        finally:
            conn.close() if conn else None

    def _create_tables(self) -> None:
        """
        Create tables in the metadata repository.
        """
        with self._connect() as conn:
            queries.create_tables(conn)

    def register(self, entry: Registry.Entry) -> None:
        """
        Register a table.
        """
        with self._connect() as conn:
            queries.register_table(
                conn,
                path=str(entry.path),
                name=entry.name,
                filetype=entry.filetype,
                schema=to_arrow_schema_bytes(entry.schema),
                rows=entry.rows,
                size=entry.size,
            )

    def unregister(self, name: str) -> None:
        """
        Unregister a table.
        """
        with self._connect() as conn:
            queries.unregister_table(conn, name=name)

    def list_all(self) -> list[Registry.Entry]:
        """
        List all tables.
        """
        with self._connect(row_type=TableRow) as conn:
            row_tuples = queries.list_tables(conn)
            return [row_tuple.to_entry() for row_tuple in row_tuples]

    def lookup(self, key: str, *, by: LookupKey) -> Registry.Entry | None:
        row_tuple: TableRow | None = None

        with self._connect(row_type=TableRow) as conn:
            match by:
                case "name":
                    # Prefer parquet to arrow if both exist.
                    row_tuple = queries.get_table(conn, name=key, filetype="parquet")
                    row_tuple = row_tuple or queries.get_table(conn, name=key, filetype="arrow")
                case "path":
                    # The string path stored in the database is native (e.g. on Win: "foo/bar" -> "foo\\bar").
                    native_path = str(Path(key))
                    row_tuple = queries.get_table_by_path(conn, path=native_path)

        if not row_tuple:
            return None

        return row_tuple.to_entry()

    def search(self, query: str = "*", *, by: SearchKey) -> list[Registry.Entry]:
        row_tuples: list[TableRow] = []
        with self._connect(row_type=TableRow) as conn:
            match by:
                case "name":
                    # Prefer parquet to arrow if both exist
                    row_tuples = list(queries.search_tables_by_name(conn, name=query))
                case "path":
                    row_tuples = list(queries.search_tables_by_path(conn, path=query))

        return [row_tuple.to_entry() for row_tuple in row_tuples]
