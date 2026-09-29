#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  cp .env.example .env
fi
need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}
if need "DB_PASSWORD"; then
  sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated DB_PASSWORD"
fi
if need "SECRET_PASSWORD"; then
  sed -i '' "s|^SECRET_PASSWORD=.*|SECRET_PASSWORD=$(openssl rand -hex 32)|" .env
  echo "  Generated SECRET"
fi
if ! grep -q "^DATABASE_URL=." .env 2>/dev/null; then
  db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
  url="postgresql://rallly:${db_pass}@rallly-db:5432/rallly"
  if grep -q "^DATABASE_URL=" .env; then
    sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=${url}|" .env
  else
    echo "DATABASE_URL=${url}" >> .env
  fi
  echo "  Generated DATABASE_URL"
fi
if ! grep -q "^POSTGRES_PASSWORD=." .env 2>/dev/null; then
  db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
  if grep -q "^POSTGRES_PASSWORD=" .env; then
    sed -i '' "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${db_pass}|" .env
  else
    echo "POSTGRES_PASSWORD=${db_pass}" >> .env
  fi
  echo "  Synced POSTGRES_PASSWORD"
fi
echo "Secrets ready."
