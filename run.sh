#!/usr/bin/env bash
# Start the todo app. One command serves both the API and the page.
set -euo pipefail
cd "$(dirname "$0")"

# .dkubex-app.env (written by `d3x app create`) sets PORT and DKUBEX_BASE_PATH in the workspace.
for f in .dkubex-app.env .env; do
  if [[ -f $f ]]; then set -a; . "./$f"; set +a; fi
done

: "${DATABASE_URL:?Set DATABASE_URL in .env (see .env.example).}"
: "${PORT:=8000}"

exec .venv/bin/uvicorn main:app --host 0.0.0.0 --port "$PORT"
