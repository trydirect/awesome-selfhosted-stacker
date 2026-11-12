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
if need "POSTGRES_PASSWORD"; then sed_inplace "s|^POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=$(openssl rand -hex 16)|" .env; echo "  Generated POSTGRES_PASSWORD"; fi
if need "N8N_ENCRYPTION_KEY"; then sed_inplace "s|^N8N_ENCRYPTION_KEY=.*|N8N_ENCRYPTION_KEY=$(openssl rand -hex 16)|" .env; echo "  Generated N8N_ENCRYPTION_KEY"; fi
if need "N8N_USER_MANAGEMENT_JWT_SECRET"; then sed_inplace "s|^N8N_USER_MANAGEMENT_JWT_SECRET=.*|N8N_USER_MANAGEMENT_JWT_SECRET=$(openssl rand -hex 16)|" .env; echo "  Generated N8N_USER_MANAGEMENT_JWT_SECRET"; fi
echo "Secrets ready."
