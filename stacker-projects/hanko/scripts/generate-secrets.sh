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
echo "Secrets ready."
