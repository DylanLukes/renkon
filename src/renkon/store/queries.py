from pathlib import Path
from sqlite3 import Connection as SQLiteConnection

import aiosql.queries


class Queries(aiosql.queries.Queries):  # type: ignore[misc]
    def get_input_table_path(self, conn: SQLiteConnection, *, name: str) -> str | None:
        ...


queries: Queries = aiosql.from_path(
    sql_path=Path(__file__).with_name("store.sql"),
    driver_adapter="sqlite3",
    queries_cls=Queries,
)
