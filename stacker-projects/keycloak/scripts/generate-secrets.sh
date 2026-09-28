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
if need "ADMIN_PASSWORD"; then
  sed -i '' "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=$(openssl rand -hex 12)|" .env
  echo "  Generated ADMIN_PASSWORD"
fi
if need "DB_PASSWORD"; then
  sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated DB_PASSWORD"
fi
db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
admin_pass=$(grep "^ADMIN_PASSWORD=" .env | cut -d= -f2-)
for pair in "KC_DB_PASSWORD:${db_pass}" "POSTGRES_PASSWORD:${db_pass}" "KEYCLOAK_ADMIN_PASSWORD:${admin_pass}" "KEYCLOAK_ADMIN:admin"; do
  key="${pair%%:*}"; val="${pair#*:}"
  if grep -q "^${key}=" .env; then
    sed -i '' "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
done
echo "  Synced KC_DB_PASSWORD/POSTGRES_PASSWORD/KEYCLOAK_ADMIN(_PASSWORD)"
echo "Secrets ready."
