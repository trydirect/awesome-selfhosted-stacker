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
if need "ENCRYPTION_KEY"; then
  val=$(openssl rand -hex 16)
  if grep -q "^ENCRYPTION_KEY=" .env; then sed -i '' "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=${val}|" .env; else echo "ENCRYPTION_KEY=${val}" >> .env; fi
  echo "  Generated ENCRYPTION_KEY"
fi
echo "Secrets ready."
