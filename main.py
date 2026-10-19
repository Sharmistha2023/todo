"""Todo list: FastAPI + PostgreSQL, one page, one table."""

import os
from contextlib import asynccontextmanager
from pathlib import Path

import psycopg
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import BaseModel

DATABASE_URL = os.environ["DATABASE_URL"]
MAX_TITLE = 200
INDEX_HTML = (Path(__file__).parent / "index.html").read_text()

pool = ConnectionPool(DATABASE_URL, min_size=1, max_size=5, open=False,
                      kwargs={"row_factory": dict_row})


@asynccontextmanager
async def lifespan(_: FastAPI):
    pool.open(wait=True)
    with pool.connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id         SERIAL PRIMARY KEY,
                title      VARCHAR(200) NOT NULL,
                completed  BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now()
            )""")
    yield
    pool.close()


# nginx forwards the full prefixed path. Setting root_path here (not uvicorn's --root-path, which
# prepends it a second time) lets routes stay declared at "/".
app = FastAPI(title="Todo", lifespan=lifespan, root_path=os.environ.get("DKUBEX_BASE_PATH", ""))

# Installed as a platform app, the DKubeX gateway authenticates the user and injects
# X-Auth-Request-User; a request without it did not come through the gateway. The chart turns
# this on. It stays off for a plain local run, where no gateway sits in front of the app.
REQUIRE_AUTH_HEADER = os.environ.get("REQUIRE_AUTH_HEADER", "").lower() in ("1", "true", "yes")


@app.middleware("http")
async def require_platform_user(request: Request, call_next):
    if (REQUIRE_AUTH_HEADER and not request.url.path.endswith("/health")
            and not request.headers.get("X-Auth-Request-User")):
        return JSONResponse({"detail": "Not authenticated"}, 401)
    return await call_next(request)


class TaskIn(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None


def clean_title(title: str) -> str:
    title = title.strip()
    if not title:
        raise HTTPException(400, "Task title cannot be empty.")
    if len(title) > MAX_TITLE:
        raise HTTPException(400, f"Task title must be {MAX_TITLE} characters or fewer.")
    return title


@app.exception_handler(RequestValidationError)
def bad_request(_: Request, __: RequestValidationError):
    return JSONResponse({"detail": "That request didn't look right. Please try again."}, 400)


@app.exception_handler(psycopg.Error)
def db_error(_: Request, __: psycopg.Error):
    return JSONResponse({"detail": "Couldn't reach the database. Please try again shortly."}, 503)


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> str:
    return INDEX_HTML.replace("__BASE_PATH__", request.scope.get("root_path", "").rstrip("/"))


@app.get("/health")
def health() -> dict:
    with pool.connection() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok"}


@app.get("/api/tasks")
def list_tasks() -> list[dict]:
    with pool.connection() as conn:
        return conn.execute(
            "SELECT id, title, completed, created_at FROM tasks ORDER BY created_at DESC, id DESC"
        ).fetchall()


@app.post("/api/tasks", status_code=201)
def add_task(task: TaskIn) -> dict:
    with pool.connection() as conn:
        return conn.execute(
            "INSERT INTO tasks (title) VALUES (%s) RETURNING id, title, completed, created_at",
            (clean_title(task.title),),
        ).fetchone()


@app.put("/api/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate) -> dict:
    title = clean_title(task.title) if task.title is not None else None
    with pool.connection() as conn:
        row = conn.execute(
            """UPDATE tasks SET title = COALESCE(%s, title), completed = COALESCE(%s, completed)
               WHERE id = %s RETURNING id, title, completed, created_at""",
            (title, task.completed, task_id),
        ).fetchone()
    if row is None:
        raise HTTPException(404, "That task no longer exists.")
    return row


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    with pool.connection() as conn:
        if conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,)).rowcount == 0:
            raise HTTPException(404, "That task no longer exists.")
