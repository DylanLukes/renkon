import os
import sys
from pathlib import Path
from typing import Any

import click
from loguru import logger

from renkon.__about__ import __version__
from renkon.config import load_config


def setup_server_logging() -> None:
    logger.remove()
    logger.add(
        sys.stderr,
        colorize=True,
        level=os.environ.get("LOG_LEVEL", "INFO"),
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> "
        "| {process} "
        "| {module}"
        "| {level} "
        "| <level>{message}</level>",
    )


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.option("-s", "--store-path", type=click.Path(), help="Path for storage")
@click.version_option(version=__version__, prog_name="renkon")
@click.pass_context
def renkon(_ctx: click.Context, store_path: Path | None) -> None:
    # Load configuration.
    config_overrides: dict[str, Any] = {"store": {}}
    if store_path:
        config_overrides["store"]["path"] = store_path

    config = load_config(update_global=True, **config_overrides)

    # Set up logging. Logging differs

    logger.info(f"Using config: {config}")


if __name__ == "__main__":
    renkon()
