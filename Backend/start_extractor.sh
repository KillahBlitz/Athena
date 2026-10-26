#!/bin/bash
# Arranca el worker del extractor: consume extractor_stream, evalúa con Jev y guarda el
# resultado en Backend/logs/. Debe correr en paralelo a start.sh (la API).

cd "$(dirname "$0")" || exit 1

source venv/bin/activate

set -a
source .env
set +a

export PYTHONPATH="$(pwd)/src:$(pwd)/../library"
export PYTHONUNBUFFERED=1

python src/tasks/extractor_event_handler.py
