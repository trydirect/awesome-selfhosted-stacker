#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "DB_PASSWORD"; then
  val=$(openssl rand -hex 16)
  if grep -q "^DB_PASSWORD=" .env; then sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=${val}|" .env; else echo "DB_PASSWORD=${val}" >> .env; fi
  echo "  Generated DB_PASSWORD"
fi
if need "REDIS_PASSWORD"; then
  val=$(openssl rand -hex 16)
  if grep -q "^REDIS_PASSWORD=" .env; then sed -i '' "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=${val}|" .env; else echo "REDIS_PASSWORD=${val}" >> .env; fi
  echo "  Generated REDIS_PASSWORD"
fi
echo "Secrets ready."
