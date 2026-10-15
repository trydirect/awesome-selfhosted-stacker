#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "WEBHOOK_SECRET"; then sed -i '' "s|^WEBHOOK_SECRET=.*|WEBHOOK_SECRET=$(openssl rand -hex 32)|" .env; echo "  Generated WEBHOOK_SECRET"; fi
if need "TOKEN_ENCRYPTION_KEY"; then sed -i '' "s|^TOKEN_ENCRYPTION_KEY=.*|TOKEN_ENCRYPTION_KEY=$(openssl rand -hex 32)|" .env; echo "  Generated TOKEN_ENCRYPTION_KEY"; fi
echo "Secrets ready."
