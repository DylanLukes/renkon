import click
from loguru import logger

from renkon.__about__ import __version__


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="renkon")
@click.option("-v", "--verbose", count=True)
@click.pass_context
def renkon(_ctx: click.Context, verbose: int) -> None:  # noqa: ARG001
    logger.debug("hello world")
