#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "AUTH_PASSWORD"; then sed -i '' "s|^AUTH_PASSWORD=.*|AUTH_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated AUTH_PASSWORD"; fi
echo "Secrets ready."
