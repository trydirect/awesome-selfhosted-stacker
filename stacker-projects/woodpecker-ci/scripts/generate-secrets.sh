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
echo "Secrets ready."
