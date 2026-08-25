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

# Portable sed in-place helper (works on both macOS and Linux)
set_secret() {
  local key="$1" val="$2"
  if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s|^${key}=.*|${key}=${val}|" .env
  else
    sed -i "s|^${key}=.*|${key}=${val}|" .env
  fi
}

if need "DB_PASSWORD"; then
  set_secret "DB_PASSWORD" "$(openssl rand -hex 16)"
  echo "  Generated DB_PASSWORD"
fi

if need "ADMIN_PASSWORD"; then
  set_secret "ADMIN_PASSWORD" "$(openssl rand -hex 16)"
  echo "  Generated ADMIN_PASSWORD"
fi

if need "SECRET_KEY"; then
  set_secret "SECRET_KEY" "$(openssl rand -hex 32)"
  echo "  Generated SECRET_KEY"
fi

if need "JWT_SECRET"; then
  set_secret "JWT_SECRET" "$(openssl rand -hex 32)"
  echo "  Generated JWT_SECRET"
fi

if need "ADMIN_TOKEN"; then
  set_secret "ADMIN_TOKEN" "$(openssl rand -hex 32)"
  echo "  Generated ADMIN_TOKEN"
fi

if need "SMTP_PASSWORD"; then
  set_secret "SMTP_PASSWORD" "$(openssl rand -hex 16)"
  echo "  Generated SMTP_PASSWORD"
fi

echo "Secrets ready."
