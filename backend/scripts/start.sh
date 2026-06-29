#!/usr/bin/env bash
# Render / production startup — migrate DB then launch API
set -euo pipefail

cd "$(dirname "$0")/.."

echo "[GrowthPilot] Running Alembic migrations..."
if alembic upgrade head; then
  echo "[GrowthPilot] Migrations applied."
else
  echo "[GrowthPilot] Migration failed — falling back to init_db via app startup."
fi

echo "[GrowthPilot] Starting uvicorn on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
