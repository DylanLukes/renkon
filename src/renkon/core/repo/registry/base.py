from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePath
from typing import Literal, Protocol, TypeAlias

import pyarrow as pa

LookupKey: TypeAlias = Literal["name", "path"]
SearchKey: TypeAlias = Literal["name", "path"]
FileType: TypeAlias = Literal["parquet", "arrow"]


class Registry(Protocol):
    @dataclass(frozen=True, kw_only=True, slots=True)
    class Entry:
        """
        Information record for a table according to the metadata registry (database).
        """

        path: PurePath
        name: str
        filetype: FileType
        schema: pa.Schema
        rows: int
        size: int

    def register(self, entry: Entry) -> None:
        ...

    def unregister(self, name: str) -> None:
        ...

    def list_all(self) -> list[Entry]:
        ...

    def lookup(self, key: str, *, by: LookupKey) -> Entry | None:
        ...

    def search(self, query: str = "*", *, by: SearchKey) -> list[Entry]:
        ...
