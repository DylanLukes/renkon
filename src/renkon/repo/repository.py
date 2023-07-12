from pathlib import PurePath

import pyarrow as pa

from renkon.repo.registry import Registry
from renkon.repo.storage import Storage


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

    def get(self, name: str) -> pa.Table | None:
        if (table_info := self.registry.lookup(name, by="name")) is None:
            return None
        return self.storage.read(table_info.path)

    def put(self, name: str, table: pa.Table, *, for_ipc: bool = False, for_storage: bool = True) -> None:
        """
        Put data into the repository.
        """
        path = PurePath(name)
        if path.suffix:
            msg = f"Name '{name}' cannot have a suffix (extension)."
            raise ValueError(msg)

        paths = []
        if not for_ipc and not for_storage:
            msg = "Cannot store data for neither IPC nor storage."
            raise ValueError(msg)

        if for_ipc:
            paths.append(path.with_suffix(".arrow"))
        if for_storage:
            paths.append(path.with_suffix(".parquet"))

        for path in paths:
            self.storage.write(path, table)
            if (table_info := self.storage.info(path)) is None:
                msg = f"Table '{name}' not found in registry immediately after store. Something is broken."
                raise LookupError(msg)
            self.registry.register(name, path, table_info)

    def exists(self, name: str) -> bool:
        """
        Check if a table exists in the repository.
        """
        return self.registry.lookup(name, by="name") is not None
