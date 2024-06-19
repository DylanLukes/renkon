from asyncio import sleep

import jinja2
import lorem
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
    words = []
    try:
        while True:
            words.append(lorem.sentence())
            text = templates.get_template("simple-list.html.jinja").render({
                "items": [
                    {"text": word} for word in words
                ]
            })
            await websocket.send_text(text)
            await sleep(1)
    except WebSocketDisconnect as dc:
        logger.info(f"Disconnecting: {dc}")

# @app.get("/todo-list")
# @jinja.hx("todo-list.html.jinja")
# async def read_todos() -> list[Todo]:
#     return TODOS
#
#
# @app.post("/todo-list")
# async def create_todo(todo: Todo) -> Todo:
#     TODOS.append(todo)
#     return todo
#
#
# @app.websocket("/todo-list/ws")
# @jinja.hx("todo-list.html.jinja")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_json()
#
#         try:
#             todo = Todo.model_validate_json(data)
#             TODOS.append(todo)
#
#         except ValueError:
#             await websocket.send_json({"error": "Invalid data"})
#             continue

# class LoremConsumer:
#     websocket: Optional[WebSocket] = None
#
#     async def connect(self, websocket: WebSocket):
#         await websocket.accept()
#         self.websocket = websocket
#
#     async def disconnect(self):
#         if self.websocket:
#             await self.websocket.close()
#             self.websocket = None
#
#     async def receive(self):
#         if self.websocket:
#             return await self.websocket.receive_text()
#         return None
