#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "DB_PASSWORD"; then sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated DB_PASSWORD"; fi
if need "ADMIN_PASSWORD"; then sed -i '' "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated ADMIN_PASSWORD"; fi
if need "SECRET_KEY"; then sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated SECRET_KEY"; fi
if need "PAPERLESS_API_TOKEN"; then sed -i '' "s|^PAPERLESS_API_TOKEN=.*|PAPERLESS_API_TOKEN=$(openssl rand -hex 16)|" .env; echo "  Generated PAPERLESS_API_TOKEN"; fi

db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
admin_pass=$(grep "^ADMIN_PASSWORD=" .env | cut -d= -f2-)
secret_key=$(grep "^SECRET_KEY=" .env | cut -d= -f2-)
for pair in "PAPERLESS_DBPASS:${db_pass}" "POSTGRES_PASSWORD:${db_pass}" "PAPERLESS_ADMIN_PASSWORD:${admin_pass}" "PAPERLESS_SECRET_KEY:${secret_key}"; do
  key="${pair%%:*}"; val="${pair#*:}"
  if grep -q "^${key}=" .env; then
    sed -i '' "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
done
echo "  Synced paperless contract keys"
echo "Secrets ready."
