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
if need "AGENT_SECRET"; then
  sed -i '' "s|^AGENT_SECRET=.*|AGENT_SECRET=$(openssl rand -hex 32)|" .env
  echo "  Generated AGENT_SECRET"
fi
if ! grep -q "^WOODPECKER_AGENT_SECRET=." .env 2>/dev/null; then
  val=$(grep "^AGENT_SECRET=" .env | cut -d= -f2-)
  [ -z "$val" ] && val=$(openssl rand -hex 16)
  if grep -q "^WOODPECKER_AGENT_SECRET=" .env; then
    sed -i '' "s|^WOODPECKER_AGENT_SECRET=.*|WOODPECKER_AGENT_SECRET=${val}|" .env
  else
    echo "WOODPECKER_AGENT_SECRET=${val}" >> .env
  fi
  echo "  Synced WOODPECKER_AGENT_SECRET"
fi
echo "Secrets ready."
