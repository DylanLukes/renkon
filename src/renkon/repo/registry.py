import atexit
import sqlite3
from sqlite3 import Connection as SQLiteConnection
from typing import Protocol

from pyarrow.fs import SubTreeFileSystem

from renkon.repo.queries import queries


class Registry(Protocol):
    pass


class SQLiteRegistry(Registry):
    """
    Handles all things related to metadata, composed by Repo.
    You should generally not need to interact with this class directly.
    """

    base_path: str
    fs: SubTreeFileSystem
    conn: SQLiteConnection

    def __init__(self, fs: SubTreeFileSystem) -> None:
        self.conn = sqlite3.connect(fs.base_path + "/metadata.db")
        atexit.register(self.conn.close)
        self._create_tables()

    def _create_tables(self, *, commit: bool = True) -> None:
        """
        Create tables in the metadata repository.
        """
        queries.create_tables(self.conn)
        if commit:
            self.conn.commit()

    def register_input(self, name: str, path: str) -> None:
        """
        Register an input table.
        """
        queries.put_input_table(self.conn, name=name, path=path)
        self.conn.commit()

    def list_input_tables(self) -> list[tuple[str, str]]:
        """
        List all input tables.
        """
        return queries.list_input_tables(self.conn)

    def lookup_input_path(self, name: str) -> str | None:
        """
        Get the path to the data file.
        """
        return queries.get_input_table_path(self.conn, name=name)