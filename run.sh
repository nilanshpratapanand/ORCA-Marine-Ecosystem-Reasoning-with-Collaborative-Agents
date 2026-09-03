#!/usr/bin/env bash
# ============================================================
#  ORCA - start backend + frontend together (Linux / macOS).
#  Run ./install-orca.sh once first. Ctrl+C stops both.
# ============================================================
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -x "backend/venv/bin/python" ]; then
  echo "Backend venv missing - run ./install-orca.sh first."
  exit 1
fi

# kill both child processes when this script exits / is Ctrl+C'd
cleanup() { kill 0 2>/dev/null || true; }
trap cleanup EXIT INT TERM

echo "[backend]  starting on http://127.0.0.1:8000"
( cd backend && source venv/bin/activate && exec python -m uvicorn app.main:app --reload ) &

sleep 2

echo "[frontend] starting on http://127.0.0.1:5173"
( cd frontend && exec npm run dev ) &

echo
echo "============================================================"
echo "  Backend:  http://127.0.0.1:8000/docs"
echo "  Frontend: http://127.0.0.1:5173"
echo "  Ctrl+C to stop both."
echo "============================================================"
wait
