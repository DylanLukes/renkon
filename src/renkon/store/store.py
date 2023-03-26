import os
from functools import lru_cache

from pyarrow import Table, fs, ipc, csv
from pyarrow import compute as pc

from renkon.config import global_config
from renkon.store.datastore import DataStore
from renkon.store.registry import Registry


class Store:
    """
    Handles all things related to storing and retrieving of data.

    Composes a DataStore and a Registry.

    Runs in its own process, with methods communicating with it via IPC (queues).
    """

    base_path: str

    data: DataStore
    metadata: Registry

    def __init__(self, base_path: str) -> None:
        self.base_path = base_path
        self.fs = fs.SubTreeFileSystem(base_path, fs.LocalFileSystem(use_mmap=True))
        self.metadata = Registry(self.fs)
        self.data = DataStore(self.fs)

    def get_input_table(self, name: str) -> Table:
        """
        Get data from the store.
        """
        # First, check if the data is in the metadata store.
        path = self.metadata.lookup_input_path(name)
        if path is None:
            raise LookupError(f"Input table '{name}' not found in metadata store.")
        return self.data.get(name)

    def put_input_table(self, name: str, data: Table) -> None:
        """
        Put data into the store.
        """
        path = self.data.put(name, data)
        self.metadata.register_input(name, path)


@lru_cache(1)
def get_store() -> Store:
    """
    Return the store.
    """
    config = global_config()
    data_dir = config.DATA_DIR

    return Store(base_path=data_dir)


if __name__ == "__main__":
    os.chdir("/Users/Dylan/PycharmProjects/renkon")
    store = get_store()

    name = "cereals-corrupt"

    local = fs.LocalFileSystem()
    data = csv.read_csv(f'etc/{name}.csv',
                        parse_options=csv.ParseOptions(delimiter=';'),
                        read_options=csv.ReadOptions(skip_rows_after_names=1))

    store.put_input_table("cereals-corrupt", data)
    data = store.get_input_table("cereals-corrupt")
    print(data)
