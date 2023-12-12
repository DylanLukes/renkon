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
from base64 import b64encode
from io import TextIOWrapper
from pathlib import Path
from typing import Any

import click
import numpy as np
import polars as pl
from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.pretty import Pretty
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from renkon.config import RenkonConfig
from renkon.core.engine import BatchInferenceEngine
from renkon.core.trait import EqualNumeric, EqualString, Linear2, Linear3, Linear4, Trait

ENABLED_TRAITS: dict[type[Trait], bool] = {
    Linear2: True,
    Linear3: True,
    Linear4: True,
    EqualNumeric: True,
    EqualString: True,
}

# Mapping from percentages to corresponding block characters.
SHADE_BLOCKS = [" ", "░", "▒", "▓", "█"]

H_BLOCK_CHARS = [" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█"]
V_BLOCK_CHARS = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]


def pct_to_block(pct: float, blocks: list[str] | None = None) -> str:
    """
    Convert a percentage to a Unicode block character, where the block height is
    proportional to the percentage.
    """
    blocks = blocks or V_BLOCK_CHARS
    return blocks[int(pct * (len(blocks) - 1))]


def mask_to_blocks(mask: pl.Series, n_chunks: int = 50) -> str:
    """
    Convert a Boolean series to a string of n_chunks Unicode block characters,
    where each character's block height is proportional to the percentage of
    True values in that chunk of the series.
    """
    chunk_pcts = (
        (
            pl.LazyFrame({"idx": pl.int_range(0, len(mask), eager=True), "mask": mask})
            .group_by_dynamic("idx", every=f"{len(mask) // n_chunks}i")
            .agg((pl.sum("mask") / pl.count("mask")).alias("pct"))
        )
        .select("pct")
        .collect()
    )["pct"].to_list()
    return "".join(map(pct_to_block, chunk_pcts))


def setup_simple_logging() -> None:
    # Add TRACE level.
    logging.addLevelName(5, "TRACE")

    if sys.stdout.isatty():
        # For interactive runs, log everything to stdout and use rich for human formatted output.
        logger.configure(
            handlers=[
                {
                    "sink": RichHandler(
                        console=Console(
                            file=sys.stdout,
                            theme=Theme(
                                {
                                    "logging.level.trace": "bold green",
                                }
                            ),
                        ),
                        markup=False,
                        show_path=True,
                        rich_tracebacks=True,
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
        # For non-interactive runs (e.g. piped into a file), log to stderr, reserving stdout for output data.
        logger.configure(
            handlers=[
                {
                    "sink": sys.stderr,
                    "level": os.environ.get("LOG_LEVEL", "INFO"),
                    "format": "{time:%F %T.%f} {level.name} {message}",
                }
            ]
        )


@click.command(context_settings={"show_default": True})
@click.argument("data_path", type=click.Path(path_type=Path, exists=True, dir_okay=False))
@click.argument("columns", type=str, nargs=-1)
@click.option(
    "-t", "--threshold", type=float, default=0.95, show_default=True, help="Score threshold for trait matches."
)
@click.pass_context
def batch(_ctx: click.Context, data_path: Path, columns: list[str], threshold: float) -> None:
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
    table = Table(title="Inference Results", show_lines=True)
    table.add_column("Sketch")
    table.add_column("Result")
    table.add_column("Score")
    table.add_column("Outliers")
    table.add_column("%")
    for col, dtype in data[columns].schema.items():
        table.add_column(f"[underline]{col}\n[/underline]{dtype}")

    if sys.stdout.isatty():
        # Nicely formatted output for interactive runs.
        for sketch, trait in sorted(results.items(), key=lambda x: x[1].score, reverse=True):
            _trait_type = sketch.trait_type
            schema = sketch.schema

            if trait.score < threshold:
                continue

            green_score_thresh = 0.5

            if trait:
                sketch_renderable = Pretty(sketch)
                trait_renderable = Text(str(trait))
                score_renderable = Text(
                    f"{trait.score:.2f}", style="green" if trait.score > green_score_thresh else "red"
                )
                outliers_renderable = Text(f"{mask_to_blocks(trait.mask.not_())}", style="red underline")
                pct_outliers_renderable = Text(f"{trait.mask.not_().sum() / trait.mask.len():.2f}", style="red")
                columns_renderables = [":heavy_check_mark:" if col in schema.columns else "" for col in columns]
            else:
                sketch_renderable = Text(f"{sketch}", style="red")
                trait_renderable = Text("n/a", style="red")
                score_renderable = Text("n/a", style="red")
                outliers_renderable = Text(" " * 50, style="red underline")
                pct_outliers_renderable = Text("n/a", style="red")
                columns_renderables = [":heavy_check_mark:" if col in schema.columns else "" for col in columns]

            table.add_row(
                sketch_renderable,
                trait_renderable,
                score_renderable,
                outliers_renderable,
                pct_outliers_renderable,
                *columns_renderables,
            )
        Console(file=sys.stdout).print(table)
    else:
        rows: list[dict[str, Any]] = []
        for sketch, trait in results.items():
            if trait is None:
                continue

            rows.append(
                {
                    "sketch": repr(sketch),
                    "trait": str(trait),
                    "score": trait.score if trait else None,
                    "outliers_b64": b64encode(np.packbits(trait.mask.not_())).decode("ascii"),
                    "outliers_pct": trait.mask.not_().sum() / trait.mask.len(),
                    **{col: col in sketch.schema.columns for col in columns},
                }
            )

        # See the comment on sys.stdout's typeshed stubs for why this is valid (unless overriden).
        if not isinstance(sys.stdout, TextIOWrapper):
            msg = "sys.stdout is not a TextIOWrapper, cannot write CSV output."
            raise RuntimeError(msg)

        # Flush stdout to ensure output is written last, just in case.
        sys.stderr.flush()

        # Write the output to stdout.
        pl.from_dicts(rows).write_csv(sys.stdout)
