#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "POSTGRES_PASSWORD"; then sed -i '' "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -hex 32)|" .env; echo "  Generated POSTGRES_PASSWORD"; fi
if need "N8N_ENCRYPTION_KEY"; then sed -i '' "s|^N8N_ENCRYPTION_KEY=.*|N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)|" .env; echo "  Generated N8N_ENCRYPTION_KEY"; fi
if need "N8N_USER_MANAGEMENT_JWT_SECRET"; then sed -i '' "s|^N8N_USER_MANAGEMENT_JWT_SECRET=.*|N8N_USER_MANAGEMENT_JWT_SECRET=$(openssl rand -hex 32)|" .env; echo "  Generated N8N_USER_MANAGEMENT_JWT_SECRET"; fi
if need "WEBUI_SECRET_KEY"; then sed -i '' "s|^WEBUI_SECRET_KEY=.*|WEBUI_SECRET_KEY=$(openssl rand -hex 32)|" .env; echo "  Generated WEBUI_SECRET_KEY"; fi
if need "FLOWISE_PASSWORD"; then sed -i '' "s|^FLOWISE_PASSWORD=.*|FLOWISE_PASSWORD=$(openssl rand -hex 32)|" .env; echo "  Generated FLOWISE_PASSWORD"; fi
echo "Secrets ready."
