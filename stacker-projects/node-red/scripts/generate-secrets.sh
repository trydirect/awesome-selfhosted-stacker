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
if need "CREDENTIAL_SECRET"; then
  sed -i '' "s|^CREDENTIAL_SECRET=.*|CREDENTIAL_SECRET=$(openssl rand -hex 32)|" .env
  echo "  Generated CREDENTIAL_SECRET"
fi
echo "Secrets ready."
