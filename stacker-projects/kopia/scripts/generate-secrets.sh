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
if need "KOPIA_PASSWORD"; then
  sed -i '' "s|^KOPIA_PASSWORD=.*|KOPIA_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated KOPIA_PASSWORD"
fi
echo "Secrets ready."
