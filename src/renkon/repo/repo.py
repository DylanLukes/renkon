from functools import lru_cache
from pathlib import Path

import polars as pl
from pyarrow import Table, fs

from renkon.config import Config, load_config
from renkon.repo.registry import Registry
from renkon.repo.store import Store


class Repo:
    """
    The repository is the state of the system, containing all submitted inputs and
    computed outputs.

    Composes/mediates a Store and a Registry.

    The Store is responsible for storing and retrieving data on disk.
    The Registry is responsible for metadata queries, such as retrieving the path
    for a given input or output result.
    """

    path: Path

    data: Store
    metadata: Registry

    def __init__(self, path: Path) -> None:
        """
        Open a repository at the given path.
        """
        self.path = path
        path.mkdir(exist_ok=True)
        root_fs = fs.SubTreeFileSystem(str(path), fs.LocalFileSystem(use_mmap=True))
        self.metadata = Registry(root_fs)
        self.data = Store(root_fs)

    def get_input_table(self, name: str) -> Table:
        """
        Get data from the repository.
        """
        # First, check if the data is in the metadata repository.
        if self.metadata.lookup_input_path(name):
            return self.data.get(name)
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
        if path := self.metadata.lookup_input_path(name):
            return Path(path)
        msg = f"Input table '{name}' not found in metadata repository."
        raise LookupError(msg)

    def put_input_table(self, name: str, data: Table) -> None:
        """
        Put data into the repository.
        """
        path = self.data.put(name, data)
        self.metadata.register_input(name, path)


@lru_cache(1)
def get_repo(config: Config | None = None) -> Repo:
    """
    Return the repository. By default, uses the global configuration, but can be
    overridden by passing a custom configuration (useful for testing, etc).
    """
    config = config or load_config()
    return Repo(path=config.repository.path)
