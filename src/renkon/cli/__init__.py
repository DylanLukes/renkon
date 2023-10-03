import click
from loguru import logger

from renkon.__about__ import __version__
from renkon.cli.simple import simple

# Disabled for now.
# from renkon.cli.client import client as client_group
# from renkon.cli.server import server as server_group


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

    # No subcommand behavior yet.
    logger.critical("not yet implemented!")


# Disabled for now.
cli.add_command(simple)
# cli.add_command(client_group)
# cli.add_command(server_group)

if __name__ == "__main__":
    cli()
