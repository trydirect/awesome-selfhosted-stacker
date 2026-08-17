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
if need "ACCESS_TOKEN_SALT"; then
  set_secret "ACCESS_TOKEN_SALT" "$(openssl rand -hex 32)"
  echo "  Generated ACCESS_TOKEN_SALT"
fi
if need "JWT_SECRET_KEY"; then
  set_secret "JWT_SECRET_KEY" "$(openssl rand -hex 32)"
  echo "  Generated JWT_SECRET_KEY"
fi
echo "Secrets ready."
