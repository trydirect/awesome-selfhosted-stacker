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

if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Created .env from .env.example"
fi

need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}

REPLACE_MASTERKEY=false
if need "ZITADEL_MASTERKEY" || grep -q "^ZITADEL_MASTERKEY=MasterkeyNeedsToHave32Characters" .env; then
  REPLACE_MASTERKEY=true
fi

if [ "$REPLACE_MASTERKEY" = true ]; then
  if grep -q "^ZITADEL_MASTERKEY=" .env 2>/dev/null; then
    sed_inplace "s|^ZITADEL_MASTERKEY=.*|ZITADEL_MASTERKEY=$(openssl rand -hex 16)|" .env
  else
    echo "ZITADEL_MASTERKEY=$(openssl rand -hex 16)" >> .env
  fi
  echo "  Generated ZITADEL_MASTERKEY"
fi

if need "POSTGRES_ADMIN_PASSWORD"; then
  sed_inplace "s|^POSTGRES_ADMIN_PASSWORD=.*|POSTGRES_ADMIN_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated POSTGRES_ADMIN_PASSWORD"
fi

echo "Secrets ready."
