#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "JWT_SECRET"; then sed -i '' "s|^JWT_SECRET=.*|JWT_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated JWT_SECRET"; fi
echo "Secrets ready."
