#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
generate_if_empty() {
  local key="$1" value
  if need "$key"; then
    value=$(openssl rand -hex 32)
    if grep -q "^${key}=" .env; then
      sed -i.bak "s|^${key}=.*|${key}=${value}|" .env && rm -f .env.bak
    else
      echo "${key}=${value}" >> .env
    fi
    echo "  Generated ${key}"
  fi
}
generate_if_empty NEO4J_PASSWORD
echo "Secrets ready."
