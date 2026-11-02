#!/usr/bin/env bash
set -e

BACKEND_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$BACKEND_DIR"

source "$BACKEND_DIR/venv/bin/activate"

set -a
source "$BACKEND_DIR/.env"
set +a

# El .env puede contener rutas de otra computadora; usar las de este checkout.
export PYTHONPATH="$BACKEND_DIR/src:$BACKEND_DIR/../library"

exec python -m uvicorn main.endpoints:api --reload --host 127.0.0.1 --port 8000
