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

from renkon.cli.tty import MIN_MATCH_GREEN, MIN_SCORE_GREEN, mask_to_blocks
from renkon.config import RenkonConfig
from renkon.core.engine import BatchInferenceEngine
from renkon.core.trait import AnyTrait, EqualNumeric, EqualString, Linear2, Linear3, Linear4
from renkon.core.trait.library.integral import Integral
from renkon.core.trait.library.negative import Negative
from renkon.core.trait.library.nonzero import Nonzero
from renkon.core.trait.library.positive import Positive

ENABLED_TRAITS: dict[type[AnyTrait], bool] = {
    Linear2: False,
    Linear3: False,
    Linear4: True,
    EqualNumeric: False,
    EqualString: False,
    Positive: False,
    Negative: False,
    Nonzero: False,
    Integral: False,
}


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
    "-ts",
    "--threshold-score",
    type=float,
    default=0.95,
    show_default=True,
    help="Score threshold for trait matches.",
)
@click.option(
    "-tm",
    "--threshold-mask",
    type=float,
    default=0.85,
    show_default=True,
    help="Mask threshold for trait matches.",
)
@click.pass_context
def batch(
    _ctx: click.Context,
    data_path: Path,
    columns: list[str],
    threshold_score: float,
    threshold_mask: float,
) -> None:
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

    # 2. Instantiate the default engine.  # TODO: use config for traits
    engine = BatchInferenceEngine(trait_types=[trait_type for trait_type, enabled in ENABLED_TRAITS.items() if enabled])
    engine.run("batch-0", data)
    results = engine.get_results("batch-0")

    # 3. Filter results. TODO

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

        def score_fn(trait: AnyTrait) -> float:
            return trait.score + (trait.mask.sum() / trait.mask.len())

        scored_results = [(sketch, trait, score_fn(trait)) for sketch, trait in results.items() if trait is not None]

        for sketch, trait, _ in sorted(scored_results, key=lambda x: x[2], reverse=True):
            _trait_type = sketch.trait_type
            schema = sketch.schema

            if trait.score <= threshold_score:
                continue

            match_pct = trait.mask.sum() / trait.mask.len()
            if match_pct <= threshold_mask:
                continue

            outlier_mask = trait.mask.not_()
            outlier_pct = outlier_mask.sum() / outlier_mask.len()

            if trait:
                sketch_renderable = Pretty(sketch)
                trait_renderable = Text(str(trait))
                score_renderable = Text(
                    f"{trait.score:.2f}",
                    style="green" if trait.score >= MIN_SCORE_GREEN else "red",
                )
                outliers_renderable = Text(f"{mask_to_blocks(outlier_mask)}", style="red underline")
                pct_outliers_renderable = Text(
                    f"{outlier_pct:.2f}",
                    style="green" if outlier_pct <= (1 - MIN_MATCH_GREEN) else "red",
                )
                columns_renderables = [":heavy_check_mark:" if col in schema.columns else "" for col in columns]
            else:
                sketch_renderable = Text(f"{sketch}", style="red")
                trait_renderable = Text("n/a", style="red")
                score_renderable = Text("n/a", style="red")
                outliers_renderable = Text(" " * 25, style="red underline")
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
                msg = "Trait is None, this should not happen."
                raise RuntimeError(msg)

            outlier_mask = trait.mask.not_()
            outlier_pct = outlier_mask.sum() / outlier_mask.len() if trait else None

            rows.append(
                {
                    "sketch": repr(sketch),
                    "trait": str(trait),
                    "score": trait.score,
                    "outliers_b64": b64encode(np.packbits(outlier_mask)).decode("ascii") if trait else None,
                    "outliers_pct": outlier_pct,
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
