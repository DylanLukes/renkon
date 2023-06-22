from functools import lru_cache
from pathlib import Path

import polars as pl
from pyarrow import Table, fs

from renkon.config import Config, get_config
from renkon.store.datastore import DataStore
from renkon.store.registry import Registry


class Store:
    """
    Handles all things related to storing and retrieving of data.

    Composes a DataStore and a Registry.

    The DataStore is responsible for storing and retrieving data on disk.
    The Registry is responsible for metadata queries, such as retrieving the path
    for a given input or output result.
    """

    root_dir: Path

    data: DataStore
    metadata: Registry

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        root_dir.mkdir(exist_ok=True)
        self.fs = fs.SubTreeFileSystem(str(root_dir), fs.LocalFileSystem(use_mmap=True))
        self.metadata = Registry(self.fs)
        self.data = DataStore(self.fs)

    def get_input_table(self, name: str) -> Table:
        """
        Get data from the store.
        """
        # First, check if the data is in the metadata store.
        if self.metadata.lookup_input_path(name):
            return self.data.get(name)
        msg = f"Input table '{name}' not found in metadata store."
        raise LookupError(msg)

    def get_input_dataframe(self, name: str) -> pl.DataFrame:
        return pl.from_arrow(self.get_input_table(name))

    def get_input_table_path(self, name: str) -> Path:
        """
        Get data from the store.
        """
        if path := self.metadata.lookup_input_path(name):
            return Path(path)
        msg = f"Input table '{name}' not found in metadata store."
        raise LookupError(msg)

    def put_input_table(self, name: str, data: Table) -> None:
        """
        Put data into the store.
        """
        path = self.data.put(name, data)
        self.metadata.register_input(name, path)


@lru_cache(1)
def get_store(config: Config | None = None) -> Store:
    """
    Return the store. By default, uses the global configuration, but can be
    overridden by passing a custom configuration (useful for testing, etc).
    """
    config = config or get_config()
    data_dir = config.store_dir

    return Store(root_dir=Path(data_dir))
