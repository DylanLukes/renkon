from functools import lru_cache
from pathlib import Path, PurePath
from typing import Literal, TypeAlias

import polars as pl
import pyarrow as pa
from pyarrow import fs as pa_fs

from renkon.config import Config, RepositoryConfig, load_config
from renkon.repo.registry import Registry, SQLiteRegistry
from renkon.repo.storage import FileSystemStorage, Storage

TableIntent: TypeAlias = Literal["processing", "storage"]


class Repository:
    """
    The repository is the state of the system, containing all submitted inputs and
    computed outputs.

    Composes/mediates a Store and a Registry.

    The Store is responsible for storing and retrieving data on disk.
    The Registry is responsible for metadata queries, such as retrieving the path
    for a given input or output result.
    """

    registry: Registry
    storage: Storage

    def __init__(self, registry: Registry, storage: Storage) -> None:
        """
        Open a repository at the given path.
        """
        self.registry = registry
        self.storage = storage

    def get_input_table(self, name: str) -> pa.Table:
        """
        Get data from the repository.
        """
        # First, check if the data is in the metadata repository.
        if self.registry.lookup_input_path(name):
            return self.storage.get(name)
        msg = f"Input table '{name}' not found in metadata repository."
        raise LookupError(msg)

    def get_input_dataframe(self, name: str) -> pl.DataFrame:
        df = pl.from_arrow(self.get_input_table(name))
        if not isinstance(df, pl.DataFrame):
            msg = f"Expected a polars.DataFrame, got {type(df)}"
            raise TypeError(msg)
        return df

    def get_input_table_path(self, name: str) -> Path:
        """
        Get data from the repository.
        """
        if path := self.registry.lookup_input_path(name):
            return Path(path)
        msg = f"Input table '{name}' not found in metadata repository."
        raise LookupError(msg)

    def put_input_table(self, name: str, data: pa.Table) -> None:
        """
        Put data into the repository.
        """
        path = self.storage.put(name, data)
        self.registry.register_input(name, path)
