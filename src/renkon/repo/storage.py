from abc import abstractmethod
from pathlib import PurePath
from typing import Protocol, TypeAlias, cast

import pyarrow as pa
import pyarrow.fs as pa_fs
import pyarrow.ipc as pa_ipc
import pyarrow.parquet as pa_pq

from renkon.repo.info import TableStat

StoragePath: TypeAlias = PurePath


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

    @abstractmethod
    def read(self, path: StoragePath) -> pa.Table | None:
        """
        Return a Table from the storage backend, or None if it does not exist.
        """
        ...

    def write(self, path: StoragePath, table: pa.Table) -> None:
        """
        Put a Table into the storage backend. Overwrites any existing data at the given path.
        """
        ...

    def delete(self, path: StoragePath) -> None:
        """
        Delete the data at the given path from the storage backend.
        """
        ...

    def info(self, path: StoragePath) -> TableStat | None:
        """
        Return a StoredTableInfo with metadata about the given table, such as
        size in bytes, number of records, etc. Useful for flights.
        """
        ...

    def exists(self, path: StoragePath) -> bool:
        """
        Return True if the path exists in the storage backend, False otherwise.
        """
        ...


class FileSystemStorage(Storage):
    """
    Abstracts details of disk storage of data away from the Repo.

    Recommended to initialize with a FileSystem with memory-mapping enabled,
    such as pyarrow.fs.LocalFileSystem(use_mmap=True), to avoid unnecessary
    memory copies (if the data is already memory-mapped by another process,
    and the OS optimizes for this).
    """

    fs: pa_fs.FileSystem

    def __init__(self, fs: pa_fs.FileSystem) -> None:
        self.fs = fs

    def read(self, path: StoragePath) -> pa.Table | None:
        match path.suffix:
            case ".parquet":
                return pa_pq.read_table(str(path), filesystem=self.fs)
            case ".arrow":
                with self.fs.open_input_file(str(path)) as file:
                    reader = pa_ipc.RecordBatchStreamReader(file)
                    table = reader.read_all()
                return table
            case _:
                msg = f"Unknown file extension: {path.suffix}"
                raise ValueError(msg)

    def write(self, path: StoragePath, table: pa.Table) -> None:
        self.fs.create_dir(str(path.parent), recursive=True)
        match path.suffix:
            case ".parquet":
                pa_pq.write_table(table, str(path), filesystem=self.fs)
            case ".arrow":
                with self.fs.open_output_stream(str(path)) as stream:
                    writer = pa_ipc.RecordBatchStreamWriter(stream, table.schema)
                    writer.write(table)
                    writer.close()
            case _:
                msg = f"Unknown file extension: {path.suffix}"
                raise ValueError(msg)

    def delete(self, path: StoragePath) -> None:
        self.fs.delete_file(str(path))

    def info(self, path: StoragePath) -> TableStat | None:
        match path.suffix:
            case ".parquet":
                schema = pa_pq.read_schema(str(path), filesystem=self.fs)
                metadata = pa_pq.read_metadata(str(path), filesystem=self.fs)
                file_info = self.fs.get_file_info(str(path))
                return TableStat(
                    path=path,
                    filetype="parquet",
                    schema=schema,
                    rows=metadata.num_rows,
                    size=file_info.size,
                )
            case ".arrow":
                with self.fs.open_input_file(str(path)) as file:
                    reader = pa_ipc.RecordBatchStreamReader(file)
                    table = reader.read_all()  # todo: ensure this plays well with use_mmap

                    return TableStat(
                        path=path,
                        filetype="arrow",
                        schema=table.schema,
                        rows=table.num_rows,
                        size=table.nbytes,
                    )
            case _:
                msg = f"Unknown file extension: {path.suffix}"
                raise ValueError(msg)

    def exists(self, path: StoragePath) -> bool:
        file_info: pa_fs.FileInfo = self.fs.get_file_info(str(path))
        return cast(bool, file_info.is_file)
