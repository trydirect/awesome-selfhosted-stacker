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
db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
url="postgres://mattermost:${db_pass}@mattermost-db:5432/mattermost?sslmode=disable"
for pair in "MM_SQLSETTINGS_DATASOURCE:${url}" "POSTGRES_PASSWORD:${db_pass}"; do
  key="${pair%%:*}"; val="${pair#*:}"
  if grep -q "^${key}=" .env; then
    sed -i '' "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
done
echo "  Generated MM_SQLSETTINGS_DATASOURCE + POSTGRES_PASSWORD"
echo "Secrets ready."
