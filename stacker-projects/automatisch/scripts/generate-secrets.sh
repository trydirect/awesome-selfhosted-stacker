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
if need "APP_SECRET_KEY"; then
  sed -i '' "s|^APP_SECRET_KEY=.*|APP_SECRET_KEY=$(openssl rand -hex 32)|" .env
  echo "  Generated APP_SECRET_KEY"
fi
if need "ENCRYPTION_KEY"; then
  sed -i '' "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$(openssl rand -hex 32)|" .env
  echo "  Generated ENCRYPTION_KEY"
fi
if need "POSTGRES_PASSWORD"; then
  sed -i '' "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated POSTGRES_PASSWORD"
fi
echo "Secrets ready."
