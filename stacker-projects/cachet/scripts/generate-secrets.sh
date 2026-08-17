#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
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
    sed -i '' "s|^${key}=.*|${key}=${val}|" .env
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
