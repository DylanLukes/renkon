from __future__ import annotations

from pathlib import Path, PurePath
from typing import TYPE_CHECKING, Any, cast

import aiosql
from aiosql.queries import Queries
from pydantic import BaseModel

from renkon.core.repo.registry.base import FileType, Registry
from renkon.core.repo.schema import from_arrow_schema_bytes

if TYPE_CHECKING:
    import sqlite3
    from sqlite3 import Connection as SQLiteConnection


class TableRow(BaseModel):
    """
    Strong typing for a table record (as a tuple) returned from the SQLite registry.

    This exists as an intermediate type between the database and the registry.
    """

    path: str
    name: str
    filetype: FileType
    schema_: bytes
    rows: int
    size: int

    @classmethod
    def row_factory(cls: type[TableRow], cur: sqlite3.Cursor, row: tuple[Any, ...]) -> TableRow:  # noqa: ARG003
        return cls(**dict(zip(TableRow.model_fields.keys(), row, strict=True)))

    def to_entry(self) -> Registry.Entry:
        """
        Convert a database entry into a registry entry.
        """
        return Registry.Entry(
            name=self.name,
            path=PurePath(self.path),
            filetype=self.filetype,
            schema=from_arrow_schema_bytes(self.schema_),  # type: ignore
            rows=self.rows,
            size=self.size,
        )


class TypedQueries(Queries):
    """
    Hack to type the queries used by the registry. This allows us to define a typed interface
    for the queries supported by the registry, and also to support mocking use of the queries in
    tests without any actual database.

    Warning: if the types in this class are changed, the corresponding types in registry.sql must
    also be changed to match, and vice versa.
    """

    def create_tables(self, conn: SQLiteConnection) -> None: ...

    def register_table(
        self,
        conn: SQLiteConnection,
        *,
        path: str,
        name: str,
        filetype: str,
        schema: bytes,
        rows: int,
        size: int,
    ) -> None: ...

    def unregister_table(self, conn: SQLiteConnection, *, name: str) -> None: ...

    def get_table(self, conn: SQLiteConnection, *, name: str, filetype: FileType) -> TableRow: ...

    def get_table_by_path(self, conn: SQLiteConnection, *, path: str) -> TableRow: ...

    def list_tables(self, conn: SQLiteConnection) -> list[TableRow]: ...

    def search_tables_by_path(self, conn: SQLiteConnection, *, path: str) -> list[TableRow]: ...

    def search_tables_by_name(self, conn: SQLiteConnection, *, name: str) -> list[TableRow]: ...


# Expose the strongly typed interface for the queries in queries.sql.
queries: TypedQueries = cast(
    TypedQueries,
    aiosql.from_path(  # type: ignore
        sql_path=Path(__file__).with_name("queries.sql"),
        queries_cls=cast(type[Queries], TypedQueries),
        driver_adapter="sqlite3",
    ),
)
