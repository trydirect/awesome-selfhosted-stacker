#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "WAHA_API_KEY"; then sed -i '' "s|^WAHA_API_KEY=.*|WAHA_API_KEY=$(openssl rand -hex 32)|" .env; echo "  Generated WAHA_API_KEY"; fi
echo "Secrets ready."
