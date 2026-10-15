#!/bin/bash
# Create .env from .env.example and fill any missing secrets.
# Safe to re-run: existing values are kept (Offen pattern).
set -euo pipefail
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  cp .env.example .env
fi

generate_if_empty() {
  local key="$1"
  local current
  current=$(grep "^${key}=" .env 2>/dev/null | cut -d= -f2- || true)
  if [ -z "${current}" ]; then
    local value
    value=$(openssl rand -hex 32)
    if grep -q "^${key}=" .env; then
      sed -i.bak "s|^${key}=.*|${key}=${value}|" .env && rm -f .env.bak
    else
      echo "${key}=${value}" >> .env
    fi
    echo "  Generated ${key}"
  fi
}

generate_if_empty API_KEY

echo "Secrets ready."
