from pyarrow import Table, ipc
from pyarrow.fs import FileSystem, SubTreeFileSystem


class Store:
    """
    Abstracts details of disk storage of data away from the Repo.

    Recommended to initialize with a FileSystem with memory-mapping enabled,
    such as pyarrow.fs.LocalFileSystem(use_mmap=True), to avoid unnecessary
    memory copies (if the data is already memory-mapped by another process,
    and the OS optimizes for this).
    """

    base_path: str
    fs: SubTreeFileSystem

    def __init__(self, fs: FileSystem) -> None:
        fs.create_dir("data", recursive=True)
        self.fs = SubTreeFileSystem("data", fs)

    def get(self, name: str) -> Table:
        """
        Get data from the repository.
        """
        with self.fs.open_input_stream(f"{name}.arrow") as stream:
            data: Table = ipc.open_stream(stream).read_all()
            return data

    def put(self, name: str, data: Table) -> str:
        """
        Put data into the repository.
        """
        with self.fs.open_output_stream(f"{name}.arrow") as stream:
            writer = ipc.new_stream(stream, data.schema)
            writer.write(data)
            writer.close()
        return f"{self.fs.base_path}{name}.arrow"
