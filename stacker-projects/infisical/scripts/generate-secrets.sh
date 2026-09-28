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
  sed -i.bak "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env && rm -f .env.bak
  echo "  Generated DB_PASSWORD"
fi
if need "ENCRYPTION_KEY"; then
  sed -i.bak "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$(openssl rand -hex 32)|" .env && rm -f .env.bak
  echo "  Generated ENCRYPTION_KEY"
fi
if need "AUTH_SECRET"; then
  sed -i.bak "s|^AUTH_SECRET=.*|AUTH_SECRET=$(openssl rand -hex 32)|" .env && rm -f .env.bak
  echo "  Generated AUTH_SECRET"
fi
if ! grep -q "^DB_CONNECTION_URI=." .env 2>/dev/null; then
  db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
  url="postgresql://infisical:${db_pass}@infisical-db:5432/infisical"
  if grep -q "^DB_CONNECTION_URI=" .env; then
    sed -i '' "s|^DB_CONNECTION_URI=.*|DB_CONNECTION_URI=${url}|" .env
  else
    echo "DB_CONNECTION_URI=${url}" >> .env
  fi
  echo "  Generated DB_CONNECTION_URI"
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
