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
if need "SECRET"; then
  sed -i '' "s|^SECRET=.*|SECRET=$(openssl rand -hex 32)|" .env
  echo "  Generated SECRET"
fi
echo "Secrets ready."
