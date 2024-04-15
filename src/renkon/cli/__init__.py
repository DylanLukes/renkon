import click

from renkon.__about__ import __version__
from renkon.cli.batch import batch


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(version=__version__, prog_name="renkon")
def cli() -> None:
    pass


cli.add_command(batch)

if __name__ == "__main__":
    cli()
