import logging

import click
import uvicorn

from renkon.util.logging import InterceptHandler, configure_logging


@click.command(context_settings={"show_default": True})
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to bind to.", type=str)
@click.option("--port", default=9876, show_default=True, help="Port to bind to.", type=int)
@click.option("--reload/--no-reload", default=True, show_default=True, help="Enable/disable auto-reload.", type=bool)
def web(host: str, port: int, reload: bool) -> None:
    configure_logging()
    uvicorn.run("renkon.web.app:app", host=host, port=port, reload=reload)
