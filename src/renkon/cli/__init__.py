import click

from renkon.__about__ import __version__


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="renkon")
@click.pass_context
def renkon(_ctx: click.Context) -> None:
    click.echo("Hello world!")
