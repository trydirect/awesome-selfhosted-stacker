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

echo "Secrets ready."
