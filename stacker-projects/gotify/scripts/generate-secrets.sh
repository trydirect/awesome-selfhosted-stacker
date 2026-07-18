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
if need "GOTIFY_DEFAULTUSER_PASS"; then
  sed -i '' "s|^GOTIFY_DEFAULTUSER_PASS=.*|GOTIFY_DEFAULTUSER_PASS=$(openssl rand -hex 12)|" .env
  echo "  Generated GOTIFY_DEFAULTUSER_PASS"
fi
echo "Secrets ready."
