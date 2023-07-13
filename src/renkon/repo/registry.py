from __future__ import annotations

import atexit
import sqlite3
from pathlib import Path, PurePath
from sqlite3 import Connection as SQLiteConnection
from typing import Literal, Protocol, TypeAlias

from renkon.repo.info import TableDBTuple, TableInfo, TableStat
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

    path: Path
    conn: SQLiteConnection

    def __init__(self, path: Path) -> None:
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = lambda cur, row: TableDBTuple(*row)
        atexit.register(self.conn.close)
        self._create_tables()

    def _create_tables(self, *, commit: bool = True) -> None:
        """
        Create tables in the metadata repository.
        """
        queries.create_tables(self.conn)
        if commit:
            self.conn.commit()

    def register(self, name: str, path: PurePath, table_info: TableStat) -> None:
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

    def list_all(self) -> list[TableInfo]:
        """
        List all tables.
        """
        values_list = queries.list_tables(self.conn)
        return [TableInfo.from_values(values) for values in values_list]

    def lookup(self, key: str, *, by: RegistryLookupKey) -> TableInfo | None:
        values = None
        match by:
            case "name":
                # Prefer parquet to arrow if both exist
                values = queries.get_table(self.conn, name=key, filetype="parquet")
                values = values or queries.get_table(self.conn, name=key, filetype="arrow")
            case "path":
                values = queries.get_table_by_path(self.conn, path=key)

        if values is None:
            return None

        return TableInfo.from_values(values)

    def search(self, query: str = "*", *, by: RegistrySearchKey) -> list[TableInfo]:
        values_list: list[TableDBTuple] = []
        match by:
            case "name":
                # Prefer parquet to arrow if both exist
                values_list = queries.search_tables_by_name(self.conn, name=query)
            case "path":
                values_list = queries.search_tables_by_path(self.conn, path=query)

        return [TableInfo.from_values(values) for values in values_list]
