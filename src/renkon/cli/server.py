import os
from pathlib import Path
from typing import Any

import click
from loguru import logger
from pyarrow import fs as pa_fs
from rich.logging import RichHandler
from rich.text import Text

from renkon.config import DEFAULTS, load_config
from renkon.core.repo import FileSystemStorage, Repository, SQLiteRegistry
from renkon.server.flight import RenkonFlightServer


def rich_iso_log_time_format(dt: Any) -> Text:
    return Text(dt.isoformat(sep=" ", timespec="milliseconds"))


def setup_server_logging() -> None:
    # todo: add support for a log file
    logger.configure(
        handlers=[
            {
                "sink": RichHandler(markup=True, log_time_format=rich_iso_log_time_format),
                "level": os.environ.get("LOG_LEVEL", "INFO"),
                "format": "{message}",
            }
        ]
    )


@click.command(context_settings={"show_default": True})
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
    setup_server_logging()

    # Repository.
    repo_path = config.repository.path
    repo_path.mkdir(parents=True, exist_ok=True)

    fs = pa_fs.SubTreeFileSystem(str(repo_path / "data"), pa_fs.LocalFileSystem(use_mmap=True))

    repository = Repository(
        registry=SQLiteRegistry(repo_path / "registry.db"),
        storage=FileSystemStorage(fs),
    )

    # Start server.
    logger.info(f"Starting Renkon server at {config.server.hostname}:{config.server.port}")
    server = RenkonFlightServer(repository, config.server)
    server.serve()
