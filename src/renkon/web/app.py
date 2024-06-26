from asyncio import sleep
from typing import cast

import jinja2
import lorem  # type: ignore
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket
from fasthx import Jinja
from loguru import logger
from starlette.websockets import WebSocketDisconnect

from renkon.util.logging import configure_logging

app = FastAPI(on_startup=[configure_logging])

# app.add_event_handler("startup", init_logging)
app.mount("/static", StaticFiles(packages=[("renkon.web", "static")]), name="static")

templates = Jinja2Templates(
    directory="templates",
    loader=jinja2.ChoiceLoader(
        [
            jinja2.FileSystemLoader("templates"),
            jinja2.PackageLoader("renkon.web", "templates"),
        ]
    ),
)
jinja = Jinja(templates)


@app.get("/")
@jinja.page("index.html.jinja")
def index():
    pass


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    words: list[str] = []
    try:
        while True:
            word = cast(str, lorem.sentence())  # type: ignore
            words.append(word)
            text = templates.get_template("simple-list.html.jinja").render(
                {"items": [{"text": word} for word in words]}
            )  # type: ignore
            await websocket.send_text(text)
            await sleep(1)
    except WebSocketDisconnect as dc:
        logger.info(f"Disconnecting: {dc}")
