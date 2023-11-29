import click

from renkon.__about__ import __version__
from renkon.cli.batch import batch


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="renkon")
@click.pass_context
def cli(ctx: click.Context) -> None:
    # If there is a subcommand, do nothing (yield to it).
    if ctx.invoked_subcommand:
        return

    ctx.invoke(batch)


cli.add_command(batch)

if __name__ == "__main__":
    cli()
