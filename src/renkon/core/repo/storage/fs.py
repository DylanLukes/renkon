"""
Filesystem based implementation of Storage.
"""
from pathlib import Path

import polars as pl
from polars import DataFrame

from renkon.core.repo.storage.base import Storage, StoragePath


class FileSystemStorage(Storage):
    """
    Abstracts details of disk storage of data away from the Repo.

    Recommended to initialize with a FileSystem with memory-mapping enabled,
    such as pyarrow.fs.LocalFileSystem(use_mmap=True), to avoid unnecessary
    memory copies (if the data is already memory-mapped by another process,
    and the OS optimizes for this).
    """

    root: Path

    def __init__(self, root: Path) -> None:
        self.root = root

    def read(self, path: StoragePath) -> DataFrame | None:
        match path.suffix:
            case ".parquet":
                return pl.read_parquet(self.root / path)
            case ".arrow":
                return pl.read_ipc(self.root / path)
            case _:
                msg = f"Unknown file extension: {path.suffix}"
                raise ValueError(msg)

    def write(self, path: StoragePath, table: DataFrame) -> None:
        (self.root / path.parent).mkdir(parents=True, exist_ok=True)

        match path.suffix:
            case ".parquet":
                table.write_parquet(self.root / path)
            case ".arrow":
                table.write_ipc(self.root / path)
            case _:
                msg = f"Unknown file extension: {path.suffix}"
                raise ValueError(msg)

    def delete(self, path: StoragePath) -> None:
        (self.root / path).unlink()

    def stat(self, path: StoragePath) -> Storage.Stat | None:
        full_path = self.root / path

        match path.suffix:
            case ".parquet":
                schema = pl.read_parquet_schema(full_path)
                row_count = pl.scan_parquet(full_path).select(pl.len()).collect().item()
                file_size = full_path.stat().st_size

                return Storage.Stat(
                    path=path,
                    filetype="parquet",
                    schema=schema,
                    rows=row_count,
                    size=file_size,
                )
            case ".arrow":
                schema = pl.read_ipc_schema(full_path)
                row_count = pl.scan_ipc(full_path).select(pl.len()).collect().item()
                file_size = full_path.stat().st_size

                return Storage.Stat(
                    path=path,
                    filetype="arrow",
                    schema=schema,
                    rows=row_count,
                    size=file_size,
                )
            case _:
                msg = f"Unknown file extension: {path.suffix}"
                raise ValueError(msg)

    def exists(self, path: StoragePath) -> bool:
        return (path := self.root / path).exists() and path.is_file()
