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
if need "NEXTAUTH_SECRET"; then
  sed_inplace "s|^NEXTAUTH_SECRET=.*|NEXTAUTH_SECRET=$(openssl rand -hex 32)|" .env
  echo "  Generated NEXTAUTH_SECRET"
fi
if need "ENCRYPTION_SECRET"; then
  sed_inplace "s|^ENCRYPTION_SECRET=.*|ENCRYPTION_SECRET=$(openssl rand -hex 32)|" .env
  echo "  Generated ENCRYPTION_SECRET"
fi
if ! grep -q "^DATABASE_URL=." .env 2>/dev/null; then
  db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
  url="postgresql://typebot:${db_pass}@typebot-db:5432/typebot"
  if grep -q "^DATABASE_URL=" .env; then
    sed_inplace "s|^DATABASE_URL=.*|DATABASE_URL=${url}|" .env
  else
    echo "DATABASE_URL=${url}" >> .env
  fi
  echo "  Generated DATABASE_URL"
fi
db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
for pair in "POSTGRES_PASSWORD:${db_pass}" "NEXTAUTH_URL:http://localhost:3001"; do
  key="${pair%%:*}"; val="${pair#*:}"
  if grep -q "^${key}=" .env; then
    sed_inplace "s|^${key}=.*|${key}=${val}|" .env
  else
    echo "${key}=${val}" >> .env
  fi
  echo "  Synced ${key}"
done
echo "Secrets ready."
