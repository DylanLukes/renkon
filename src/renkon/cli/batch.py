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
from rich.logging import RichHandler

from renkon.config import RenkonConfig
from renkon.core.engine import BatchInferenceEngine
from renkon.core.trait import Linear4


def setup_simple_logging() -> None:
    # Minimal RichHandler logging, with just the level and message.
    logger.configure(
        handlers=[
            {
                "sink": RichHandler(markup=True),
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
    engine = BatchInferenceEngine(trait_types=[Linear4])
    engine.run("batch-0", data)
    traits = engine.get_results("batch-0")

    # 3. Output results.
    for _trait in traits:
        pass

    # # _engine = SimpleEngine() todo
    # trait_type: TraitType | None = None
    #
    # # 2. Handle default package case.
    # if "." not in trait_name:
    #     trait_name = "renkon.core.trait." + trait_name
    #
    # # 3. Locate the trait and ensure it exists.
    # try:
    #     trait_type = loader.load(trait_name)
    # except TraitLoaderError as err:
    #     msg = f"Trait '{trait_name}' not found."
    #     raise click.BadParameter(msg) from err
    # logger.info(f"Loaded trait '{trait_name}'")
    #
    # # 4 Sketch the trait.
    # sketch = trait_type.sketch(columns)
    # logger.info(f"Sketched trait: {sketch}")
    #
    # # 5. Try to load the data.
    # data = pl.read_csv(data_path)
    # logger.info(f"Loaded data:\n{data}")
    #
    # # 6 Ensure that the columns exist and are of acceptable types.
    # for col, valid_dtypes in zip(columns, trait_type.supported_dtypes(len(columns)), strict=True):
    #     if col not in data.columns:
    #         msg = f"Column '{col}' not found in data."
    #         raise RuntimeError(msg)
    #
    #     if data[col].dtype not in valid_dtypes:
    #         msg = (
    #             f"Column '{col} is of unsupported type '{data[col].dtype}', "
    #             f"expected: '{' | '.join([str(t) for t in valid_dtypes])}'."
    #         )
    #         raise RuntimeError(msg)
    #
    # # 7. Run inference.
    #
    # # 8. Output results.
    # pass
