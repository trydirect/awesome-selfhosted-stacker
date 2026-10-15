#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "SURREAL_USER"; then sed -i '' "s|^SURREAL_USER=.*|SURREAL_USER=$(openssl rand -hex 32)|" .env; echo "  Generated SURREAL_USER"; fi
if need "SURREAL_PASSWORD"; then sed -i '' "s|^SURREAL_PASSWORD=.*|SURREAL_PASSWORD=$(openssl rand -hex 32)|" .env; echo "  Generated SURREAL_PASSWORD"; fi
if need "OPEN_NOTEBOOK_ENCRYPTION_KEY"; then sed -i '' "s|^OPEN_NOTEBOOK_ENCRYPTION_KEY=.*|OPEN_NOTEBOOK_ENCRYPTION_KEY=$(openssl rand -hex 32)|" .env; echo "  Generated OPEN_NOTEBOOK_ENCRYPTION_KEY"; fi
if need "OPEN_NOTEBOOK_PASSWORD"; then sed -i '' "s|^OPEN_NOTEBOOK_PASSWORD=.*|OPEN_NOTEBOOK_PASSWORD=$(openssl rand -hex 32)|" .env; echo "  Generated OPEN_NOTEBOOK_PASSWORD"; fi
echo "Secrets ready."
