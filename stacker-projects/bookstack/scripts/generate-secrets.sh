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
if need "DB_PASSWORD"; then
  sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated DB_PASSWORD"
fi
if need "DB_ROOT_PASSWORD"; then
  sed -i '' "s|^DB_ROOT_PASSWORD=.*|DB_ROOT_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated DB_ROOT_PASSWORD"
fi
if ! grep -q "^APP_KEY=." .env 2>/dev/null; then
  echo "APP_KEY=base64:$(openssl rand -base64 32 | tr -d '=/\n')" >> .env
  echo "  Generated APP_KEY"
fi
# Build the container .env (image ignores DB_* environment variables)
if grep -q "^DB_PASSWORD=." .env 2>/dev/null && grep -q "^APP_KEY=." .env 2>/dev/null; then
  dbp=$(grep "^DB_PASSWORD=" .env | cut -d= -f2-)
  akey=$(grep "^APP_KEY=" .env | cut -d= -f2-)
  cat > bookstack.env <<EOF2
APP_KEY=${akey}
APP_URL=http://localhost:6875
DB_HOST=bookstack-db
DB_PORT=3306
DB_DATABASE=bookstack
DB_USERNAME=bookstack
DB_PASSWORD=${dbp}
EOF2
  cp bookstack.env .stacker/bookstack.env 2>/dev/null || true
  echo "  Generated bookstack.env"
fi
echo "Secrets ready."
