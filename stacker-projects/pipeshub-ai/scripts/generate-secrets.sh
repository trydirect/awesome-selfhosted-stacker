#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

# `sed -i` is not portable: BSD sed (macOS) wants the backup suffix as a
# separate argument, GNU sed (Linux) takes it attached or not at all, and each
# rejects the other's form. `sed -i '' ...` worked on a laptop and died on
# every server with
#     sed: can't read s|...|: No such file or directory
# so the secrets were silently never generated. Decide once, here.
if sed --version >/dev/null 2>&1; then
  sed_inplace() { sed -i "$@"; }      # GNU sed, Linux
else
  sed_inplace() { sed -i '' "$@"; }   # BSD sed, macOS
fi
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "NEO4J_PASSWORD"; then sed_inplace "s|^NEO4J_PASSWORD=.*|NEO4J_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated NEO4J_PASSWORD"; fi
if need "MONGO_PASSWORD"; then sed_inplace "s|^MONGO_PASSWORD=.*|MONGO_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated MONGO_PASSWORD"; fi
if need "REDIS_PASSWORD"; then sed_inplace "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated REDIS_PASSWORD"; fi
if need "QDRANT_API_KEY"; then sed_inplace "s|^QDRANT_API_KEY=.*|QDRANT_API_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated QDRANT_API_KEY"; fi
if need "SECRET_KEY"; then sed_inplace "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated SECRET_KEY"; fi
if need "JWT_SECRET"; then sed_inplace "s|^JWT_SECRET=.*|JWT_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated JWT_SECRET"; fi
if need "SCOPED_JWT_SECRET"; then sed_inplace "s|^SCOPED_JWT_SECRET=.*|SCOPED_JWT_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated SCOPED_JWT_SECRET"; fi
if need "COOKIE_SECRET"; then sed_inplace "s|^COOKIE_SECRET=.*|COOKIE_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated COOKIE_SECRET"; fi
echo "Secrets ready."
