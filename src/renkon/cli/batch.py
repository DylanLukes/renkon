"""
Simple single trait inference. No task graphs, no dependant inference, no multi-processing. Just
runs a single trait inference on a single dataset for specified columns.

It is assumed that the data provided is already in a sane format and requires no
special pre-processing (no extra rows to trim, types can be inferred automatically, etc).

This is likely a temporary feature but is useful for testing and for small-scale inference.
"""
import os
from pathlib import Path

import click
import polars as pl
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from renkon.config import RenkonConfig
from renkon.core.engine import BatchInferenceEngine
from renkon.core.trait import *


def setup_simple_logging() -> None:
    # Minimal RichHandler logging, with just the level and message.
    logger.configure(
        handlers=[
            {
                "sink": RichHandler(
                    markup=False,
                    show_path=False,
                    rich_tracebacks=True,
                    # tracebacks_suppress=[click],
                    tracebacks_show_locals=True,
                ),
                "level": os.environ.get("LOG_LEVEL", "INFO"),
                "format": "{message}",
            }
        ]
    )


@click.command(context_settings={"show_default": True})
@click.argument("data_path", type=click.Path(path_type=Path, exists=True, dir_okay=False))
@click.argument("columns", type=str, nargs=-1)
@click.pass_context
def batch(_ctx: click.Context, data_path: Path, columns: list[str]) -> None:
    data = pl.read_csv(data_path, columns=columns or None)
    columns = columns or data.columns

    # 0. Configure logging.
    setup_simple_logging()
    logger.info("Logging enabled.")
    logger.trace("Trace")

    # 1. Load the configuration.
    _config = RenkonConfig.load()

    # 2. Instantiate the default engine.  # todo: use config for traits
    engine = BatchInferenceEngine(trait_types=[Linear4, EqualNumeric])
    engine.run("batch-0", data)
    results = engine.get_results("batch-0")

    # 3. Output results.
    table = Table(title="Inference Results")
    table.add_column("Trait", style="green")
    table.add_column("Result")
    for col in columns:
        table.add_column(f"[italic]{col}")

    console = Console()
    for sketch, trait in sorted(results.items()):
        trait_type = sketch.trait_type
        schema = sketch.schema

        table.add_row(
            f"{sketch.trait_type.__name__}",
            str(trait),
            *[":heavy_check_mark:" if col in schema.columns else "" for col in columns],
        )

    console.print(table)
