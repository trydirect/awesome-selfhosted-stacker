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

[ ! -f .env ] && cp .env.example .env && echo "  Created .env from .env.example"

need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}

if need "APP_KEY"; then
  sed_inplace "s|^APP_KEY=.*|APP_KEY=base64:$(openssl rand -base64 32)|" .env
  echo "  Generated APP_KEY"
fi

if need "DB_PASSWORD"; then
  sed_inplace "s/^DB_PASSWORD=.*/DB_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated DB_PASSWORD"
fi

if need "REDIS_PASSWORD"; then
  sed_inplace "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated REDIS_PASSWORD"
fi

if need "PUSHER_APP_SECRET"; then
  sed_inplace "s/^PUSHER_APP_SECRET=.*/PUSHER_APP_SECRET=$(openssl rand -hex 16)/" .env
  echo "  Generated PUSHER_APP_SECRET"
fi

echo "Secrets ready."
