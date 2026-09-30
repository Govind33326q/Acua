#!/usr/bin/env bash
# AquaVisionaries - start on macOS / Linux.
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8001}"
PY="${PYTHON:-python3}"
if [ ! -x ".venv/bin/python" ]; then
  echo "Creating virtual environment..."
  "$PY" -m venv .venv
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
fi
if [ ! -f frontend/dist/index.html ]; then
  echo "frontend/dist is missing. Build it: (cd frontend && npm install && npm run build)"; exit 1
fi
echo "AquaVisionaries: http://127.0.0.1:${PORT}/  (Ctrl+C to stop)"
exec .venv/bin/python -m uvicorn src.api:app --host 127.0.0.1 --port "$PORT"
