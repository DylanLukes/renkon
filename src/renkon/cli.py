import atexit
import os
from pathlib import Path
from typing import Any, cast

import click
import pyarrow as pa
import pyarrow.fs as pa_fs
from loguru import logger
from pyarrow import csv as pa_csv
from pyarrow import ipc as pa_ipc
from pyarrow import parquet as pa_pq
from rich.logging import RichHandler

from renkon.__about__ import __version__
from renkon.client import RenkonFlightClient
from renkon.config import DEFAULTS, load_config
from renkon.repo import FileSystemStorage, Repository
from renkon.repo.registry import SQLiteRegistry
from renkon.server import RenkonFlightServer


def setup_default_logging() -> None:
    logger.configure(
        handlers=[
            {
                "sink": RichHandler(log_time_format=lambda dt: dt.isoformat(sep=" ", timespec="milliseconds")),
                "level": os.environ.get("LOG_LEVEL", "INFO"),
                "format": "{message}",
            }
        ]
    )


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="renkon")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Starts a renkon server as a subprocess, and then connects a client to it.

    This is intended to be used only by an end-user for inspecting a repository,
    and is started with the default configuration. For real-world use, please
    use the server and client subcommands.

    If you must override the configuration, `renkon.toml` is loaded from the current working directory.

    By default, renkon runs on 127.0.0.1:1410, and uses the repository .renkon in the current working directory.
    """
    # If there is a subcommand, do nothing.
    if ctx.invoked_subcommand:
        return

    # No subcommand behavior.
    setup_default_logging()
    logger.critical("not yet implemented!")


@cli.command(context_settings={"show_default": True})
@click.argument("hostname", type=str, default=DEFAULTS["server"]["hostname"])
@click.argument("port", type=int, default=DEFAULTS["server"]["port"])
@click.option(
    "-d",
    "--data-dir",
    type=click.Path(path_type=Path),
    default=DEFAULTS["repository"]["path"],
    help="Path for data repository",
)
@click.pass_context
def server(_ctx: click.Context, hostname: str, port: int, data_dir: Path) -> None:
    # Configuration.
    config_overrides: dict[str, Any] = {
        "repository": {
            "path": data_dir.resolve(),
        },
        "server": {
            "hostname": hostname,
            "port": port,
        },
    }

    config = load_config(update_global=True, **config_overrides)

    # Logging.
    setup_default_logging()

    # Repository.
    repo_path = config.repository.path
    repo_path.mkdir(parents=True, exist_ok=True)

    fs = pa_fs.SubTreeFileSystem(str(repo_path / "data"), pa_fs.LocalFileSystem(use_mmap=True))

    repository = Repository(
        registry=SQLiteRegistry(repo_path / "metadata.db"),
        storage=FileSystemStorage(fs),
    )

    # Start server.
    logger.info(f"Starting Renkon server at {config.server.hostname}:{config.server.port}")
    server = RenkonFlightServer(repository, config.server)
    server.serve()


@cli.group(context_settings={"show_default": True})
@click.option("--hostname", "-H", type=str, default=DEFAULTS["server"]["hostname"])
@click.option("--port", "-P", type=int, default=DEFAULTS["server"]["port"])
@click.pass_context
def client(ctx: click.Context, hostname: str, port: int) -> None:
    # Logging.
    setup_default_logging()

    # Start client.
    client = RenkonFlightClient(location=f"grpc://{hostname}:{port}")

    logger.info(f"Connecting to {hostname}:{port}...")
    client.wait_for_available()
    logger.info("Connected!")

    ctx.obj = client

    atexit.register(client.close)

    # logger.info("Uploading test data (cereals-corrupt.csv)...")
    # table = csv.read_csv("etc/samples/cereals-corrupt.csv",
    #                      read_options=csv.ReadOptions(skip_rows_after_names=1),
    #                      parse_options=csv.ParseOptions(delimiter=";"),
    #                      convert_options=csv.ConvertOptions(auto_dict_encode=True))
    # client.upload("test", table)
    #
    # logger.info("Downloading test data...")
    # table = client.download("test")
    # logger.info(pretty_repr(table, expand_all=True))
    #
    # client.close()


@client.command(context_settings={"show_default": True})
@click.argument("name", type=str)
@click.argument("path", type=click.Path(path_type=Path, exists=True, dir_okay=False))
@click.pass_context
def put(ctx: click.Context, name: str, path: Path) -> None:
    client = cast(RenkonFlightClient, ctx.obj)

    table: pa.Table
    match path.suffix.lower():
        case ".csv":
            table = pa_csv.read_csv(path)
        case ".parquet":
            table = pa_pq.read_table(path)
        case ".arrow":
            table = pa_ipc.open_file(path).read_all()
        case _:
            msg = f"Unsupported file type: {path.suffix}"
            raise ValueError(msg)

    client.upload(name, table)
    logger.info(f"Uploaded {name}!")


@client.command(context_settings={"show_default": True})
@click.argument("name", type=str)
@click.argument("path", type=click.Path(path_type=Path, exists=False, dir_okay=False))
@click.pass_context
def get(ctx: click.Context, name: str, path: Path) -> None:
    client = cast(RenkonFlightClient, ctx.obj)

    if path.is_dir():
        logger.warning(f"Path {path} is a directory, defaulting to {path}/{name}.parquet")
        path.mkdir(parents=True, exist_ok=True)
        path = path / f"{name}.parquet"

    try:
        table = client.download(name)
        match path.suffix.lower():
            case ".csv":
                pa_csv.write_csv(table, path)
            case ".parquet":
                pa_pq.write_table(table, path)
            case ".arrow":
                pa_ipc.new_file(path, table.schema).write_all(table)
            case _:
                msg = f"Unsupported file type: {path.suffix}"
                raise ValueError(msg)
        logger.info(f"Downloaded {name} to {path}")
    except pa.ArrowKeyError:
        logger.error(f"Dataset {name} does not exist!")


if __name__ == "__main__":
    cli()
