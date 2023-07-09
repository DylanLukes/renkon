import os
from pathlib import Path
from typing import Any

import click
from loguru import logger
from pyarrow.flight import FlightClient
from rich.logging import RichHandler
from rich.pretty import pprint

from renkon.__about__ import __version__
from renkon.client import RenkonFlightClient
from renkon.config import DEFAULTS, load_config
from renkon.repo import get_repo
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
@click.option(
    "-d", "--data-dir", type=click.Path(), default=DEFAULTS["repository"]["path"], help="Path for data repository"
)
@click.version_option(version=__version__, prog_name="renkon")
@click.pass_context
def cli(ctx: click.Context, data_dir: Path) -> None:
    """
    Starts a renkon server as a subprocess, and then connects a client to it.

    This is intended for convenience, and is started with the default configuration.

    To override the configuration, use the `server` command, `renkon.toml` configuration, or (todo) environment variables.

    By default, renkon runs on 127.0.0.1:1410, and stores data in .renkon in the current working directory.
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
    "-d", "--data-dir", type=click.Path(), default=DEFAULTS["repository"]["path"], help="Path for data repository"
)
@click.pass_context
def server(_ctx: click.Context, hostname: str, port: int, data_dir: Path) -> None:
    # Configuration.
    config_overrides: dict[str, Any] = {
        "repository": {
            "path": data_dir,
        },
        "server": {
            "hostname": hostname,
            "port": port,
        },
    }

    config = load_config(update_global=True, **config_overrides)

    # Logging.
    setup_default_logging()

    # Store initialization.
    if not config.repository.path.exists():
        config.repository.path.mkdir(parents=True, exist_ok=True)
    store = get_repo(config)

    # Start server.
    logger.info(f"Starting Renkon server at {config.server.hostname}:{config.server.port}")
    server = RenkonFlightServer(store, config.server)
    server.serve()


@cli.command(context_settings={"show_default": True})
@click.argument("hostname", type=str)
@click.argument("port", type=int)
@click.pass_context
def client(_ctx: click.Context, hostname: str, port: int) -> None:
    # Logging.
    setup_default_logging()

    # Start client.
    # client = FlightClient(location=f"grpc://{hostname}:{port}")
    client = RenkonFlightClient(location=f"grpc://{hostname}:{port}")
    #
    logger.info(f"Connecting to {hostname}:{port}...")
    client.wait_for_available()
    logger.info("Connected!")
    client.close()


if __name__ == "__main__":
    cli()
