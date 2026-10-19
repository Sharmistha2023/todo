# Todo

A minimal todo list: FastAPI backend, PostgreSQL storage, one HTML page with plain JavaScript.
The `tasks` table is created automatically at startup.

## Run

```sh
cp .env.example .env          # then set DATABASE_URL for your PostgreSQL database
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
bash run.sh                   # serves the page and the API on 0.0.0.0:$PORT (default 8000)
```

No Docker is required by the app itself; it only needs a reachable PostgreSQL server.

## API

- `GET /api/tasks` — list tasks, newest first
- `POST /api/tasks` — add a task: `{"title": "..."}`
- `PUT /api/tasks/{id}` — update a task: `{"title": "..."}` and/or `{"completed": true}`
- `DELETE /api/tasks/{id}` — delete a task
- `GET /health` — database connectivity check

## Package as a DKubeX app

`Dockerfile` builds the image (listens on `$PORT`, default 8080). `charts/todo/` is the Helm
chart for the DKubeX catalog:

- Routed at `/todo` through the shared gateway with `cookie-auth` (`templates/httproute.yaml`).
- Declares the `postgres` dependency; DKubeX provisions the database and injects
  `postgres.db_url`, which becomes `DATABASE_URL`.
- Sets `REQUIRE_AUTH_HEADER=true`, so any request without `X-Auth-Request-User` gets a 401
  (except `/health`, used by the readiness probe).
- The page follows the platform theme in `localStorage['dkubex-ui-theme']`.

```sh
docker build -t ghcr.io/dkubeio/todo:0.1.0 . && docker push ghcr.io/dkubeio/todo:0.1.0
python3 ~/.claude/skills/package-app/scripts/validate_chart.py charts/todo
```
