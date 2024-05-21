from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal, Protocol

type LookupKey = Literal["name", "path"]
type SearchKey = Literal["name", "path"]
type FileType = Literal["parquet", "arrow"]

if TYPE_CHECKING:
    from pathlib import PurePath

    from polars.type_aliases import SchemaDict


class Registry(Protocol):
    @dataclass(frozen=True, kw_only=True, slots=True)
    class Entry:
        """
        Information record for a table according to the metadata registry (database).
        """

        path: PurePath
        name: str
        filetype: FileType
        schema: SchemaDict
        rows: int
        size: int

    def register(self, entry: Entry) -> None: ...

    def unregister(self, name: str) -> None: ...

    def list_all(self) -> list[Entry]: ...

    def lookup(self, key: str, *, by: LookupKey) -> Entry | None: ...

    def search(self, query: str = "*", *, by: SearchKey) -> list[Entry]: ...
