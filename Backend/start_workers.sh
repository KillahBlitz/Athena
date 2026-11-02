#!/usr/bin/env bash
set -e

BACKEND_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$BACKEND_DIR"

source "$BACKEND_DIR/venv/bin/activate"

set -a
source "$BACKEND_DIR/.env"
set +a

export PYTHONPATH="$BACKEND_DIR/src:$BACKEND_DIR/../library"
export PYTHONUNBUFFERED=1

if [ "$#" -eq 0 ]; then
    WORKERS=(classifier extractor constructor)
else
    WORKERS=("$@")
fi

for name in "${WORKERS[@]}"; do
    if [ ! -f "src/tasks/${name}_event_handler.py" ]; then
        echo "Worker desconocido: '$name' (opciones: classifier, extractor, constructor)" >&2
        exit 1
    fi
done

declare -A NAMES=()
PIDS=()

cleanup() {
    trap - INT TERM EXIT
    for pid in "${PIDS[@]}"; do
        kill "$pid" 2>/dev/null || true
    done
    wait 2>/dev/null || true
    echo "Workers detenidos."
}
trap 'cleanup; exit 130' INT TERM
trap cleanup EXIT

for name in "${WORKERS[@]}"; do
    python "src/tasks/${name}_event_handler.py" > >(sed -u "s/^/[$name] /") 2>&1 &
    PIDS+=("$!")
    NAMES[$!]="$name"
    echo "[$name] iniciado (pid $!)"
done
echo "El classifier tarda ~1 min en entrenar antes de consumir eventos. Ctrl+C para detener."

set +e
wait -n -p finished "${PIDS[@]}"
status=$?
echo "El worker '${NAMES[${finished:-0}]:-?}' terminó con código $status; deteniendo los demás." >&2
exit "$status"
