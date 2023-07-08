import os
from pathlib import Path
from typing import Any

import click
from loguru import logger
from rich.logging import RichHandler

from renkon.__about__ import __version__
from renkon.config import DEFAULTS, load_config
from renkon.server import RenkonFlightServer
from renkon.store import get_store


def setup_server_logging() -> None:
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
def cli(_ctx: click.Context) -> None:
    pass


@cli.command(context_settings={"show_default": True})
@click.argument("hostname", type=str, default=DEFAULTS["server"]["hostname"])
@click.argument("port", type=int, default=DEFAULTS["server"]["port"])
@click.option("-s", "--store-path", type=click.Path(), default=DEFAULTS["store"]["path"], help="Path for data store")
@click.pass_context
def server(_ctx: click.Context, hostname: str, port: int, store_path: Path | None) -> None:
    # Configuration.
    config_overrides: dict[str, Any] = {
        "store": {},
        "server": {
            "hostname": hostname,
            "port": port,
        },
    }

    if store_path:
        config_overrides["store"]["path"] = store_path

    config = load_config(update_global=True, **config_overrides)

    # Logging.
    setup_server_logging()

    # Store initialization.
    if not config.store.path.exists():
        config.store.path.mkdir(parents=True, exist_ok=True)
    store = get_store(config)

    # Start server.
    logger.info(f"Starting Renkon server at {config.server.hostname}:{config.server.port}")
    server = RenkonFlightServer(store, config.server)
    server.serve()


if __name__ == "__main__":
    cli()
