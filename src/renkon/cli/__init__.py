import os
from pathlib import Path
from typing import Any

import click
from loguru import logger
from rich.logging import RichHandler

from renkon.__about__ import __version__
from renkon.config import DEFAULTS, load_config
from renkon.repo import get_repo
from renkon.server import RenkonFlightServer


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
@click.option(
    "-d", "--data-dir", type=click.Path(), default=DEFAULTS["repository"]["path"], help="Path for data repository"
)
@click.pass_context
def server(_ctx: click.Context, hostname: str, port: int, data_dir: Path | None) -> None:
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
    setup_server_logging()

    # Store initialization.
    if not config.repository.path.exists():
        config.repository.path.mkdir(parents=True, exist_ok=True)
    store = get_repo(config)

    # Start server.
    logger.info(f"Starting Renkon server at {config.server.hostname}:{config.server.port}")
    server = RenkonFlightServer(store, config.server)
    server.serve()


if __name__ == "__main__":
    cli()
