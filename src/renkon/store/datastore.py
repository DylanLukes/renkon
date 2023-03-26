from pyarrow import Table, ipc
from pyarrow._fs import SubTreeFileSystem, FileSystem


class DataStore:
    """
    Handles all things related to data, composed by Store.
    """
    base_path: str
    fs: SubTreeFileSystem

    def __init__(self, fs: FileSystem) -> None:
        fs.create_dir(f"data", recursive=True)
        self.fs = SubTreeFileSystem("data", fs)

    def get(self, name: str) -> Table:
        """
        Get data from the store.
        """
        with self.fs.open_input_stream(f"{name}.arrow") as stream:
            data: Table = ipc.open_stream(stream).read_all()
            return data

    def put(self, name: str, data: Table) -> str:
        """
        Put data into the store.
        """
        with self.fs.open_output_stream(f"{name}.arrow") as stream:
            writer = ipc.new_stream(stream, data.schema)
            writer.write(data)
            writer.close()
        return f"{self.fs.base_path}{name}.arrow"
