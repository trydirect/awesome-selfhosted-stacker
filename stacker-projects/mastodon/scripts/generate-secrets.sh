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

if need "SECRET_KEY_BASE"; then
  set_secret "SECRET_KEY_BASE" "$(openssl rand -hex 64)"
  echo "  Generated SECRET_KEY_BASE"
fi

if need "OTP_SECRET"; then
  set_secret "OTP_SECRET" "$(openssl rand -base64 32)"
  echo "  Generated OTP_SECRET"
fi

if need "VAPID_PRIVATE_KEY"; then
  set_secret "VAPID_PRIVATE_KEY" "$(openssl rand -hex 32)"
  echo "  Generated VAPID_PRIVATE_KEY"
fi

if need "VAPID_PUBLIC_KEY"; then
  set_secret "VAPID_PUBLIC_KEY" "$(openssl rand -hex 32)"
  echo "  Generated VAPID_PUBLIC_KEY"
fi

if need "ACTIVE_RECORD_ENCRYPTION_DETERMINISTIC_KEY"; then
  set_secret "ACTIVE_RECORD_ENCRYPTION_DETERMINISTIC_KEY" "$(openssl rand -hex 32)"
  echo "  Generated ACTIVE_RECORD_ENCRYPTION_DETERMINISTIC_KEY"
fi

if need "ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT"; then
  set_secret "ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT" "$(openssl rand -hex 16)"
  echo "  Generated ACTIVE_RECORD_ENCRYPTION_KEY_DERIVATION_SALT"
fi

if need "ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY"; then
  set_secret "ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY" "$(openssl rand -hex 32)"
  echo "  Generated ACTIVE_RECORD_ENCRYPTION_PRIMARY_KEY"
fi

echo "Secrets ready."
