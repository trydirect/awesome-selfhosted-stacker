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
  sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated DB_PASSWORD"
fi
if need "NEXTAUTH_SECRET"; then
  sed -i '' "s|^NEXTAUTH_SECRET=.*|NEXTAUTH_SECRET=$(openssl rand -hex 32)|" .env
  echo "  Generated NEXTAUTH_SECRET"
fi
if need "CALENDSO_ENCRYPTION_KEY"; then
  sed -i '' "s|^CALENDSO_ENCRYPTION_KEY=.*|CALENDSO_ENCRYPTION_KEY=$(openssl rand -hex 32)|" .env
  echo "  Generated CALENDSO_ENCRYPTION_KEY"
fi
echo "Secrets ready."
