#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "NEO4J_PASSWORD"; then sed -i '' "s|^NEO4J_PASSWORD=.*|NEO4J_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated NEO4J_PASSWORD"; fi
if need "MONGO_PASSWORD"; then sed -i '' "s|^MONGO_PASSWORD=.*|MONGO_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated MONGO_PASSWORD"; fi
if need "REDIS_PASSWORD"; then sed -i '' "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated REDIS_PASSWORD"; fi
if need "QDRANT_API_KEY"; then sed -i '' "s|^QDRANT_API_KEY=.*|QDRANT_API_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated QDRANT_API_KEY"; fi
if need "SECRET_KEY"; then sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated SECRET_KEY"; fi
if need "JWT_SECRET"; then sed -i '' "s|^JWT_SECRET=.*|JWT_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated JWT_SECRET"; fi
if need "SCOPED_JWT_SECRET"; then sed -i '' "s|^SCOPED_JWT_SECRET=.*|SCOPED_JWT_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated SCOPED_JWT_SECRET"; fi
if need "COOKIE_SECRET"; then sed -i '' "s|^COOKIE_SECRET=.*|COOKIE_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated COOKIE_SECRET"; fi
echo "Secrets ready."
