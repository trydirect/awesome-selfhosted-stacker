#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "POSTGRES_PASSWORD"; then sed -i '' "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated POSTGRES_PASSWORD"; fi
for kv in LIGHTRAG_API_KEY:16 LIGHTRAG_ADMIN_PASSWORD:12 TOKEN_SECRET:24; do
  k=${kv%%:*}; n=${kv##*:}
  if need "$k"; then sed -i '' "s|^$k=.*|$k=$(openssl rand -hex "$n")|" .env; echo "  Generated $k"; fi
done
echo "Secrets ready."
