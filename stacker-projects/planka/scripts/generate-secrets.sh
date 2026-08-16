#!/bin/bash
set -euo pipefail
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
if need "DB_PASSWORD"; then
  sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated DB_PASSWORD"
fi
if need "SECRET_KEY"; then
  sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 32)|" .env
  echo "  Generated SECRET_KEY"
fi
echo "Secrets ready."
