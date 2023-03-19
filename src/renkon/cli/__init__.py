# SPDX-FileCopyrightText: 2023-present Dylan Lukes <lukes.dylan@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import click

from ..__about__ import __version__


@click.group(context_settings={'help_option_names': ['-h', '--help']}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name='renkon')
@click.pass_context
def renkon(ctx: click.Context):
    click.echo('Hello world!')
