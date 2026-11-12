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
set_secret() {
  local key="$1" val="$2"
  if [ "$(uname)" = "Darwin" ]; then
    sed_inplace "s|^${key}=.*|${key}=${val}|" .env
  else
    sed -i "s|^${key}=.*|${key}=${val}|" .env
  fi
}
if need "DB_PASSWORD"; then
  set_secret "DB_PASSWORD" "$(openssl rand -hex 16)"
  echo "  Generated DB_PASSWORD"
fi
if need "DB_ROOT_PASSWORD"; then
  set_secret "DB_ROOT_PASSWORD" "$(openssl rand -hex 16)"
  echo "  Generated DB_ROOT_PASSWORD"
fi
if need "APP_KEY"; then
  set_secret "APP_KEY" "$(openssl rand -hex 32)"
  echo "  Generated APP_KEY"
fi
echo "Secrets ready."
