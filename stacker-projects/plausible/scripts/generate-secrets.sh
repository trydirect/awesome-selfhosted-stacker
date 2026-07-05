#!/bin/bash
set -euo pipefail

# Generate secrets for first deploy. Fills empty values in .env,
# skips if already populated (re-deploys keep existing secrets).

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

if need "SECRET_KEY_BASE"; then
  sed -i '' "s/^SECRET_KEY_BASE=.*/SECRET_KEY_BASE=$(openssl rand -hex 64)/" .env
  echo "  Generated SECRET_KEY_BASE"
fi

if need "DB_PASSWORD"; then
  sed -i '' "s/^DB_PASSWORD=.*/DB_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated DB_PASSWORD"
fi

if need "TOTP_VAULT_KEY"; then
  sed -i '' "s/^TOTP_VAULT_KEY=.*/TOTP_VAULT_KEY=$(openssl rand -base64 32)/" .env
  echo "  Generated TOTP_VAULT_KEY"
fi

echo "Secrets ready."
