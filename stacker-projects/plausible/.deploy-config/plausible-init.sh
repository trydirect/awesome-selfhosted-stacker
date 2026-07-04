#!/bin/sh
# Auto-bootstrap plausible databases before starting.
set -e

echo "[plausible-init] Waiting for Postgres..."
until pg_isready -h plausible_db -U postgres -d plausible 2>/dev/null; do
  sleep 2
done
echo "[plausible-init] Postgres is ready."

echo "[plausible-init] Creating ClickHouse database..."
for i in $(seq 1 30); do
  if wget -qO- "http://plausible_events_db:8123/?query=CREATE+DATABASE+IF+NOT+EXISTS+plausible" 2>/dev/null; then
    break
  fi
  sleep 2
done
echo "[plausible-init] ClickHouse ready."

echo "[plausible-init] Running migrations..."
/entrypoint.sh db createdb
/entrypoint.sh db migrate

echo "[plausible-init] Starting Plausible..."
exec /entrypoint.sh run
