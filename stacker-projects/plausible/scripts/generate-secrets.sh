#!/bin/bash
set -euo pipefail

# Generate secrets for first deploy. Fills empty values in .env,
# skips if already populated (re-deploys keep existing secrets).

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

if need "SECRET_KEY_BASE"; then
  sed_inplace "s/^SECRET_KEY_BASE=.*/SECRET_KEY_BASE=$(openssl rand -hex 64)/" .env
  echo "  Generated SECRET_KEY_BASE"
fi

if need "DB_PASSWORD"; then
  sed_inplace "s/^DB_PASSWORD=.*/DB_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated DB_PASSWORD"
fi

if need "TOTP_VAULT_KEY"; then
  sed_inplace "s|^TOTP_VAULT_KEY=.*|TOTP_VAULT_KEY=$(openssl rand -base64 32)|" .env
  echo "  Generated TOTP_VAULT_KEY"
fi

echo "Secrets ready."
