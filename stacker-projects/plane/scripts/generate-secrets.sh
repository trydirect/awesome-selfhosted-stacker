#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
gen() {
  local name=$1 bytes=$2
  if need "$name"; then
    val=$(openssl rand -hex "$bytes")
    if grep -q "^$name=" .env; then sed -i '' "s|^$name=.*|$name=${val}|" .env; else echo "$name=${val}" >> .env; fi
    echo "  Generated $name"
  fi
}
gen DB_PASSWORD 16
gen MQ_PASSWORD 12
gen SECRET_KEY 24
echo "Secrets ready."
