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
for kv in LIGHTRAG_API_KEY:16 LIGHTRAG_ADMIN_PASSWORD:12 TOKEN_SECRET:24; do
  k=${kv%%:*}; n=${kv##*:}
  if need "$k"; then sed_inplace "s|^$k=.*|$k=$(openssl rand -hex "$n")|" .env; echo "  Generated $k"; fi
done
echo "Secrets ready."
