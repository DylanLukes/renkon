"""
Filesystem based implementation of Storage.
"""

from typing import cast

import pyarrow as pa
from pyarrow import fs as pa_fs
from pyarrow import ipc as pa_ipc
from pyarrow import parquet as pa_pq

from renkon.core.repo.storage.base import Storage, StoragePath


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

    def stat(self, path: StoragePath) -> Storage.Stat | None:
        match path.suffix:
            case ".parquet":
                schema = pa_pq.read_schema(str(path), filesystem=self.fs)
                metadata = pa_pq.read_metadata(str(path), filesystem=self.fs)
                file_info = self.fs.get_file_info(str(path))
                return Storage.Stat(
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

                    return Storage.Stat(
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
