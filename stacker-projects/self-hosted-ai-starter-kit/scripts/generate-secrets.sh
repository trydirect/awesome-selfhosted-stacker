#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "POSTGRES_PASSWORD"; then sed -i '' "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated POSTGRES_PASSWORD"; fi
if need "N8N_ENCRYPTION_KEY"; then sed -i '' "s|^N8N_ENCRYPTION_KEY=.*|N8N_ENCRYPTION_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated N8N_ENCRYPTION_KEY"; fi
if need "N8N_USER_MANAGEMENT_JWT_SECRET"; then sed -i '' "s|^N8N_USER_MANAGEMENT_JWT_SECRET=.*|N8N_USER_MANAGEMENT_JWT_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated N8N_USER_MANAGEMENT_JWT_SECRET"; fi
echo "Secrets ready."
