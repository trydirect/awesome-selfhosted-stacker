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

REPLACE_MASTERKEY=false
if need "ZITADEL_MASTERKEY" || grep -q "^ZITADEL_MASTERKEY=MasterkeyNeedsToHave32Characters" .env; then
  REPLACE_MASTERKEY=true
fi

if [ "$REPLACE_MASTERKEY" = true ]; then
  if grep -q "^ZITADEL_MASTERKEY=" .env 2>/dev/null; then
    sed -i '' "s|^ZITADEL_MASTERKEY=.*|ZITADEL_MASTERKEY=$(openssl rand -hex 16)|" .env
  else
    echo "ZITADEL_MASTERKEY=$(openssl rand -hex 16)" >> .env
  fi
  echo "  Generated ZITADEL_MASTERKEY"
fi

if need "POSTGRES_ADMIN_PASSWORD"; then
  sed -i '' "s|^POSTGRES_ADMIN_PASSWORD=.*|POSTGRES_ADMIN_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated POSTGRES_ADMIN_PASSWORD"
fi

echo "Secrets ready."
