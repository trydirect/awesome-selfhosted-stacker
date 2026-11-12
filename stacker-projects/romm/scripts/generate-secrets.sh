#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

# `sed -i` is not portable: BSD sed (macOS) wants the backup suffix as a
# separate argument, GNU sed (Linux) takes it attached or not at all, and each
# rejects the other's form. `sed -i '' ...` worked on a laptop and died on
# every server with
#     sed: can't read s|...|: No such file or directory
# so the secrets were silently never generated. Decide once, here.
if sed --version >/dev/null 2>&1; then
  sed_inplace() { sed -i "$@"; }      # GNU sed, Linux
else
  sed_inplace() { sed -i '' "$@"; }   # BSD sed, macOS
fi

[ ! -f .env ] && cp .env.example .env && echo "  Created .env from .env.example"

need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}

if need "DB_PASSWD"; then
  sed_inplace "s/^DB_PASSWD=.*/DB_PASSWD=$(openssl rand -hex 16)/" .env
  echo "  Generated DB_PASSWD"
fi

if need "MARIADB_ROOT_PASSWORD"; then
  sed_inplace "s/^MARIADB_ROOT_PASSWORD=.*/MARIADB_ROOT_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated MARIADB_ROOT_PASSWORD"
fi

if need "ROMM_AUTH_SECRET_KEY"; then
  sed_inplace "s/^ROMM_AUTH_SECRET_KEY=.*/ROMM_AUTH_SECRET_KEY=$(openssl rand -hex 32)/" .env
  echo "  Generated ROMM_AUTH_SECRET_KEY"
fi

if ! grep -q "^MARIADB_PASSWORD=." .env 2>/dev/null; then
  db_pass=$(grep "^DB_PASSWD=" .env | cut -d= -f2-)
  if grep -q "^MARIADB_PASSWORD=" .env; then
    sed_inplace "s|^MARIADB_PASSWORD=.*|MARIADB_PASSWORD=${db_pass}|" .env
  else
    echo "MARIADB_PASSWORD=${db_pass}" >> .env
  fi
  echo "  Synced MARIADB_PASSWORD"
fi
echo "Secrets ready."
