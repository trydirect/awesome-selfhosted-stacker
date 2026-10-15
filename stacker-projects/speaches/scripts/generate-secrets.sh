#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "API_KEY"; then sed -i '' "s|^API_KEY=.*|API_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated API_KEY"; fi
echo "Secrets ready."
