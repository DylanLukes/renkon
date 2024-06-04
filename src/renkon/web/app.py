from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.websockets import WebSocket
from fasthx import Jinja
from pydantic import BaseModel

# TEMPLATES_DIR = pkg_resources('')


class Todo(BaseModel):
    text: str


# Actual state in this demo
TODOS = [
    Todo(text="Buy milk"),
    Todo(text="Buy eggs"),
    Todo(text="Buy bread"),
]

app = FastAPI()

jinja = Jinja(Jinja2Templates("templates"))


@app.get("/")
@jinja.page("index.html.jinja")
def index():
    pass


@app.get("/todo-list")
@jinja.hx("todo-list.html.jinja")
async def read_todos() -> list[Todo]:
    return TODOS


#
@app.post("/todo-list")
async def create_todo(todo: Todo) -> Todo:
    TODOS.append(todo)
    return todo


@app.websocket("/todo-list/ws")
@jinja.hx("todo-list.html.jinja")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_json()

        try:
            todo = Todo.model_validate_json(data)
            TODOS.append(todo)

        except ValueError:
            await websocket.send_json({"error": "Invalid data"})
            continue
