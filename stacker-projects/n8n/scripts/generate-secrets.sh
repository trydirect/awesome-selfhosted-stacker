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
for pair in POSTGRES_PASSWORD:16 N8N_ENCRYPTION_KEY:16 ADMIN_PASSWORD:12; do
  key="${pair%%:*}"; bytes="${pair#*:}"
  if need "$key"; then
    sed -i '' "s|^${key}=.*|${key}=$(openssl rand -hex "$bytes")|" .env
    echo "  Generated ${key}"
  fi
done
if need "ADMIN_EMAIL"; then
  echo "  Set ADMIN_EMAIL in .env: it is your n8n owner login"
fi
