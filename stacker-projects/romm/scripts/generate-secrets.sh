#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

[ ! -f .env ] && cp .env.example .env && echo "  Created .env from .env.example"

need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}

if need "DB_PASSWD"; then
  sed -i '' "s/^DB_PASSWD=.*/DB_PASSWD=$(openssl rand -hex 16)/" .env
  echo "  Generated DB_PASSWD"
fi

if need "MARIADB_ROOT_PASSWORD"; then
  sed -i '' "s/^MARIADB_ROOT_PASSWORD=.*/MARIADB_ROOT_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated MARIADB_ROOT_PASSWORD"
fi

if need "ROMM_AUTH_SECRET_KEY"; then
  sed -i '' "s/^ROMM_AUTH_SECRET_KEY=.*/ROMM_AUTH_SECRET_KEY=$(openssl rand -hex 32)/" .env
  echo "  Generated ROMM_AUTH_SECRET_KEY"
fi

if ! grep -q "^MARIADB_PASSWORD=." .env 2>/dev/null; then
  db_pass=$(grep "^DB_PASSWD=" .env | cut -d= -f2-)
  if grep -q "^MARIADB_PASSWORD=" .env; then
    sed -i '' "s|^MARIADB_PASSWORD=.*|MARIADB_PASSWORD=${db_pass}|" .env
  else
    echo "MARIADB_PASSWORD=${db_pass}" >> .env
  fi
  echo "  Synced MARIADB_PASSWORD"
fi
echo "Secrets ready."
