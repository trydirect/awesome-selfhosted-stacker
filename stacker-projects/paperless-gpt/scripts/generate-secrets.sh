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
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "DB_PASSWORD"; then sed_inplace "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated DB_PASSWORD"; fi
if need "ADMIN_PASSWORD"; then sed_inplace "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated ADMIN_PASSWORD"; fi
if need "SECRET_KEY"; then sed_inplace "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated SECRET_KEY"; fi
if need "PAPERLESS_API_TOKEN"; then sed_inplace "s|^PAPERLESS_API_TOKEN=.*|PAPERLESS_API_TOKEN=$(openssl rand -hex 16)|" .env; echo "  Generated PAPERLESS_API_TOKEN"; fi

db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
admin_pass=$(grep "^ADMIN_PASSWORD=" .env | cut -d= -f2-)
secret_key=$(grep "^SECRET_KEY=" .env | cut -d= -f2-)
for pair in "PAPERLESS_DBPASS:${db_pass}" "POSTGRES_PASSWORD:${db_pass}" "PAPERLESS_ADMIN_PASSWORD:${admin_pass}" "PAPERLESS_SECRET_KEY:${secret_key}"; do
  key="${pair%%:*}"; val="${pair#*:}"
  if grep -q "^${key}=" .env; then
    sed_inplace "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
done
echo "  Synced paperless contract keys"
echo "Secrets ready."
