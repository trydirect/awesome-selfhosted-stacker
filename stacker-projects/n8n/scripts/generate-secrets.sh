#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Created .env from .env.example"
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
if need "ADMIN_PASSWORD"; then
  sed -i '' "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated ADMIN_PASSWORD"
fi
db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
admin_pass=$(grep "^ADMIN_PASSWORD=" .env | cut -d= -f2-)
for pair in "DB_POSTGRESDB_PASSWORD:${db_pass}" "POSTGRES_PASSWORD:${db_pass}" "N8N_BASIC_AUTH_PASSWORD:${admin_pass}" "N8N_BASIC_AUTH_USER:admin" "N8N_BASIC_AUTH_ACTIVE:true"; do
  key="${pair%%:*}"; val="${pair#*:}"
  if grep -q "^${key}=" .env; then
    sed -i '' "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
done
echo "  Synced n8n contract keys"
echo "Secrets ready."
