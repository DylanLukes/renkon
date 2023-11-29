from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from pathlib import PurePath
from typing import Protocol

from polars import DataFrame
from polars.type_aliases import SchemaDict

from renkon.core.repo import Registry
from renkon.core.repo.registry.base import FileType

type StoragePath = PurePath


class Storage(Protocol):  # pragma: no cover
    """
    Protocol for a storage backend for a :class:`renkon.repo.Repo`.

    A storage backend is responsible for storing and retrieving data from e.g. disk. It is not
    concerned with metadata, nor the contents of the data itself. It is however concerned with
    the format of the data, and how it is stored on disk (or elsewhere).

    The storage backend furthermore is not aware of the choice of dataframe library (Polars, Python, etc)
    and deals strictly in Arrow Tables.

    The purpose of this abstraction is to allow for different storage backends to be used, and to
    abstract storage-level details such as storage format away from usage-level abstractions such as
    intended usage (processing, storage, etc).
    """

    @dataclass(frozen=True, kw_only=True, slots=True)
    class Stat:
        """
        Information about a table in storage, produced by the storage backend
        from the underlying data.

        Contains most of the same information as a Registry.Entry, except the
        name of the table in the registry, which may not match the name in the
        storage (on disk, on some remote storage, etc).

        :field path: Logical path to the table in storage.
        :field filetype: Filetype of the table, either "parquet" or "arrow".
        :field schema: Schema of the table.
        :field rows: Number of rows in the table, or -1 if unknown.
        :field size: Size of the serialized table in bytes, or -1 if unknown.
        """

        path: PurePath
        filetype: FileType
        schema: SchemaDict
        rows: int = -1
        size: int = -1

        def to_entry(self, name: str) -> Registry.Entry:
            """
            Convert a TableStat object into a TableInfo object.
            """
            return Registry.Entry(
                name=name,
                path=self.path,
                filetype=self.filetype,
                schema=self.schema,
                rows=self.rows,
                size=self.size,
            )

    @abstractmethod
    def read(self, path: StoragePath) -> DataFrame | None:
        """
        Return a Table from the storage backend, or None if it does not exist.
        """
        ...

    def write(self, path: StoragePath, table: DataFrame) -> None:
        """
        Put a Table into the storage backend. Overwrites any existing data at the given path.
        """
        ...

    def delete(self, path: StoragePath) -> None:
        """
        Delete the data at the given path from the storage backend.
        """
        ...

    def stat(self, path: StoragePath) -> Stat | None:
        """
        Return a TableStat with metadata about the given table, such as
        size in bytes, number of records, etc. Useful for flights.
        """
        ...

    def exists(self, path: StoragePath) -> bool:
        """
        Return True if the path exists in the storage backend, False otherwise.
        """
        ...
