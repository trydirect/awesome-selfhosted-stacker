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
if [ ! -f .env ]; then
  cp .env.example .env
fi
need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}
if need "DB_PASSWORD"; then
  sed_inplace "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated DB_PASSWORD"
fi
if need "SECRET_KEY_BASE"; then
  sed_inplace "s|^SECRET_KEY_BASE=.*|SECRET_KEY_BASE=$(openssl rand -hex 64)|" .env
  echo "  Generated SECRET_KEY_BASE"
fi
if need "POSTGRES_PASSWORD"; then
  db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
  if grep -q "^POSTGRES_PASSWORD=" .env; then
    sed_inplace "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${db_pass}|" .env
  else
    echo "POSTGRES_PASSWORD=${db_pass}" >> .env
  fi
  echo "  Generated POSTGRES_PASSWORD"
fi
if need "DATABASE_URL"; then
  db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
  url="postgresql://chatwoot:${db_pass}@chatwoot-db:5432/chatwoot"
  if grep -q "^DATABASE_URL=" .env; then
    sed_inplace "s|^DATABASE_URL=.*|DATABASE_URL=${url}|" .env
  else
    echo "DATABASE_URL=${url}" >> .env
  fi
  echo "  Generated DATABASE_URL"
fi
echo "Secrets ready."
