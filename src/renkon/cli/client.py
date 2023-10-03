import atexit
import os
from pathlib import Path
from typing import cast

import click
import pyarrow as pa
from loguru import logger
from pyarrow import csv as pa_csv
from pyarrow import ipc as pa_ipc
from pyarrow import parquet as pa_pq
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from renkon.client.flight import RenkonFlightClient
from renkon.config import DEFAULTS


def setup_client_logging() -> None:
    # Minimal RichHandler logging, with just the level and message.
    logger.configure(
        handlers=[
            {
                "sink": RichHandler(markup=True, show_time=False, show_level=True, show_path=False),
                "level": os.environ.get("LOG_LEVEL", "INFO"),
                "format": "{message}",
            }
        ]
    )


@click.group(context_settings={"show_default": True})
@click.option("--hostname", "-H", type=str, default=DEFAULTS["server"]["hostname"])
@click.option("--port", "-P", type=int, default=DEFAULTS["server"]["port"])
@click.pass_context
def client(ctx: click.Context, hostname: str, port: int) -> None:
    # Logging.
    setup_client_logging()

    # Start client.
    client = RenkonFlightClient(location=f"grpc://{hostname}:{port}")

    logger.info(f"Connecting to {hostname}:{port}...")
    client.wait_for_available()
    logger.info("Connected!")

    ctx.obj = client

    atexit.register(client.close)


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


def abbrev_type(type_: pa.DataType) -> str:
    # If a dictionary, format recursively...
    if isinstance(type_, pa.DictionaryType):
        return f"{{{abbrev_type(type_.index_type)}: {abbrev_type(type_.value_type)}}}"
    # If a list, format recursively...
    if isinstance(type_, pa.ListType):
        return f"[{abbrev_type(type_.value_type)}]"
    # Otherwise, just return the type name.
    return str(type_)


@client.command(name="list", context_settings={"show_default": True})
@click.pass_context
def list_(ctx: click.Context) -> None:
    client = cast(RenkonFlightClient, ctx.obj)

    console = Console()

    flights = client.list_flights()
    for flight in flights:
        table = Table(title=flight.descriptor.path[0].decode(), show_header=True, header_style="bold")
        for col in flight.schema:
            table.add_column(col.name)
        # Add a row containing the abbreviated types of each column.
        table.add_row(*[abbrev_type(col.type) for col in flight.schema])
        console.print(table)

    pass
