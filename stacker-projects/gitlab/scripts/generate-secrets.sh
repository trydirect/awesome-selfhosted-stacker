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

if need "GITLAB_ROOT_PASSWORD"; then
  sed -i '' "s|^GITLAB_ROOT_PASSWORD=.*|GITLAB_ROOT_PASSWORD=$(openssl rand -hex 24)|" .env
  echo "  Generated GITLAB_ROOT_PASSWORD"
fi

if need "SECRET_KEY_BASE"; then
  sed -i '' "s|^SECRET_KEY_BASE=.*|SECRET_KEY_BASE=$(openssl rand -hex 64)|" .env
  echo "  Generated SECRET_KEY_BASE"
fi

if need "OTP_SECRET"; then
  sed -i '' "s|^OTP_SECRET=.*|OTP_SECRET=$(openssl rand -base64 32)|" .env
  echo "  Generated OTP_SECRET"
fi

echo "Secrets ready."
