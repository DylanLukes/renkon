import click
from loguru import logger

from renkon.__about__ import __version__
from renkon.cli.client import client as client_group
from renkon.cli.server import server as server_group


@click.group(
    context_settings={"help_option_names": ["-h", "--help"]},
    invoke_without_command=True,
)
@click.version_option(version=__version__, prog_name="renkon")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Starts a renkon server as a subprocess, and then connects a client to it.

    This is intended to be used only by an end-user for inspecting a repository,
    and is started with the default configuration. For real-world use, please
    use the server and client subcommands.

    If you must override the configuration, `renkon.toml` is loaded from the current working directory.

    By default, renkon runs on 127.0.0.1:1410, and uses the repository .renkon in the current working directory.
    """
    # If there is a subcommand, do nothing.
    if ctx.invoked_subcommand:
        return

    # No subcommand behavior.
    logger.critical("not yet implemented!")


cli.add_command(client_group)
cli.add_command(server_group)

if __name__ == "__main__":
    cli()
