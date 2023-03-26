import atexit
import sqlite3
from pathlib import Path
from sqlite3 import Connection as SQLiteConnection

import aiosql
from pyarrow.fs import SubTreeFileSystem


class Registry:
    """
    Handles all things related to metadata, composed by Store.

    Uses DuckDB as a backing for a metadata file.
    """
    base_path: str
    fs: SubTreeFileSystem
    conn: SQLiteConnection

    def __init__(self, fs: SubTreeFileSystem) -> None:
        self.conn = sqlite3.connect(fs.base_path + "/metadata.db")
        atexit.register(self.conn.close)
        self._create_tables()

    def _create_tables(self, commit=True) -> None:
        """
        Create tables in the metadata store.
        """
        queries.create_tables(self.conn)

    def register_input(self, name: str, path: str) -> None:
        """
        Register an input table.
        """
        x = queries.put_input_table(self.conn, name=name, path=path)
        self.conn.commit()

    def lookup_input_path(self, name: str) -> str | None:
        """
        Get the path to the data file.
        """
        return queries.get_input_table_path(self.conn, name=name)


queries = aiosql.from_path(Path(__file__).with_name("store.sql"), "sqlite3")
