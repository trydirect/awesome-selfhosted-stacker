#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "DB_PASSWORD"; then sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated DB_PASSWORD"; fi
if need "AUTHENTICATION_API_KEY"; then sed -i '' "s|^AUTHENTICATION_API_KEY=.*|AUTHENTICATION_API_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated AUTHENTICATION_API_KEY"; fi
echo "Secrets ready."
