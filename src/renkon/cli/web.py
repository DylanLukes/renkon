import click
import uvicorn

from renkon.web.app import app


@click.command(context_settings={"show_default": True})
@click.option("--host", default="127.0.0.1", show_default=True, help="Host to bind to.", type=str)
@click.option("--port", default=9876, show_default=True, help="Port to bind to.", type=int)
def web(host: str, port: int) -> None:
    uvicorn.run(app, host=host, port=port)
