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
  sed -i.bak "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env && rm -f .env.bak
  echo "  Generated DB_PASSWORD"
fi
if need "SECRETS_DEFAULT"; then
  sed -i.bak "s|^SECRETS_DEFAULT=.*|SECRETS_DEFAULT=$(openssl rand -hex 32)|" .env && rm -f .env.bak
  echo "  Generated SECRETS_DEFAULT"
fi

# Generate config.yaml with actual secrets
DB_PASSWORD=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
SECRETS_DEFAULT=$(grep "^SECRETS_DEFAULT=" .env | cut -d= -f2-)

cat > config.yaml << EOF
server:
  port: 8000
  public_port: 8000
  env: production
  webauthn:
    relying_party:
      id: localhost
database:
  host: hanko-db
  port: 5432
  user: hanko
  password: ${DB_PASSWORD}
  database: hanko
  dialect: postgres
secrets:
  default: ${SECRETS_DEFAULT}
EOF

if need "HANKO_DATABASE_PASSWORD" || need "POSTGRES_PASSWORD"; then
  db_pass=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
  for key in HANKO_DATABASE_PASSWORD POSTGRES_PASSWORD; do
    if grep -q "^${key}=" .env; then
      sed_inplace "s|^${key}=.*|${key}=${db_pass}|" .env
    else
      echo "${key}=${db_pass}" >> .env
    fi
  done
  echo "  Synced HANKO_DATABASE_PASSWORD/POSTGRES_PASSWORD to DB_PASSWORD"
fi
echo "Secrets ready."
