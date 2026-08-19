#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  cp .env.example .env
fi
need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}
set_secret() {
  sed -i.bak "s|^$1=.*|$1=$2|" .env && rm -f .env.bak
  echo "  Generated $1"
}
if need "DB_PASSWORD"; then set_secret "DB_PASSWORD" "$(openssl rand -hex 16)"; fi
if need "SECRET_KEY"; then set_secret "SECRET_KEY" "$(openssl rand -hex 16)"; fi
if need "API_KEY"; then set_secret "API_KEY" "$(openssl rand -hex 16)"; fi
if need "ADMIN_PASSWORD"; then set_secret "ADMIN_PASSWORD" "$(openssl rand -hex 16)"; fi
if need "KESTRA_PASSWORD"; then set_secret "KESTRA_PASSWORD" "$(openssl rand -hex 16)"; fi
echo "Secrets ready."
