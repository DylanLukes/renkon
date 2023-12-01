"""
Simple single trait inference. No task graphs, no dependant inference, no multi-processing. Just
runs a single trait inference on a single dataset for specified columns.

It is assumed that the data provided is already in a sane format and requires no
special pre-processing (no extra rows to trim, types can be inferred automatically, etc).

This is likely a temporary feature but is useful for testing and for small-scale inference.
"""
import logging
import os
import sys
from pathlib import Path

import click
import polars as pl
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.theme import Theme

from renkon.config import RenkonConfig
from renkon.core.engine import BatchInferenceEngine
from renkon.core.trait import EqualNumeric, EqualString, Linear2, Linear3, Linear4, Trait

ENABLED_TRAITS: dict[type[Trait], bool] = {
    Linear2: False,
    Linear3: False,
    Linear4: False,
    EqualNumeric: True,
    EqualString: True,
}

logging.addLevelName(5, "TRACE")
console = Console(
    theme=Theme(
        {
            "logging.level.trace": "bold green",
        }
    )
)


def setup_simple_logging() -> None:
    if sys.stdout.isatty():
        # Prettified logging for interactive runs in a TTY.
        logger.configure(
            handlers=[
                {
                    "sink": RichHandler(
                        console=console,
                        markup=False,
                        show_path=True,
                        rich_tracebacks=True,
                        # Format with iso8601 timestamps.
                        omit_repeated_times=True,
                        tracebacks_suppress=[click],
                        tracebacks_show_locals=True,
                    ),
                    "level": os.environ.get("LOG_LEVEL", "INFO"),
                    "format": "{message}",
                    "backtrace": False,  # rich will handle this instead
                }
            ]
        )
    else:
        # Simple logging for non-interactive runs.
        logger.configure(
            handlers=[
                {
                    "sink": sys.stdout,
                    "level": os.environ.get("LOG_LEVEL", "INFO"),
                    "format": "{time:%F %T.%f} {level.name} {message}",
                }
            ]
        )


@click.command(context_settings={"show_default": True})
@click.argument("data_path", type=click.Path(path_type=Path, exists=True, dir_okay=False))
@click.argument("columns", type=str, nargs=-1)
@click.pass_context
def batch(_ctx: click.Context, data_path: Path, columns: list[str]) -> None:
    data = pl.read_csv(data_path, columns=columns or None)
    data = data.select(columns)  # reorder to match input
    columns = list(columns or data.columns)

    # 0. Configure logging.
    setup_simple_logging()
    logger.info("Logging enabled.")
    logger.debug("Debug logging enabled.")
    logger.trace("Trace logging enabled.")

    # 1. Load the configuration.
    _config = RenkonConfig.load()

    # 2. Instantiate the default engine.  # todo: use config for traits
    engine = BatchInferenceEngine(trait_types=[trait_type for trait_type, enabled in ENABLED_TRAITS.items() if enabled])
    engine.run("batch-0", data)
    results = engine.get_results("batch-0")

    # 3. Output results.
    table = Table(title="Inference Results")
    table.add_column("Class", style="green")
    table.add_column("Result")
    table.add_column("Score")
    table.add_column("Match")
    for col, dtype in data[columns].schema.items():
        table.add_column(f"[underline]{col}\n[/underline]{dtype}")

    for sketch, trait in results.items():
        _trait_type = sketch.trait_type
        schema = sketch.schema

        table.add_row(
            f"{sketch.trait_type.__name__}",
            str(trait),
            f"{trait.score:0.3f}",
            "",
            *[":heavy_check_mark:" if col in schema.columns else "" for col in columns],
        )

    console.print(table)
