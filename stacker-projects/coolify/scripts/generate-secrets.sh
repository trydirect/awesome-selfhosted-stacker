#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."

[ ! -f .env ] && cp .env.example .env && echo "  Created .env from .env.example"

need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}

if need "APP_KEY"; then
  sed -i '' "s/^APP_KEY=.*/APP_KEY=base64:$(openssl rand -base64 32)/" .env
  echo "  Generated APP_KEY"
fi

if need "DB_PASSWORD"; then
  sed -i '' "s/^DB_PASSWORD=.*/DB_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated DB_PASSWORD"
fi

if need "REDIS_PASSWORD"; then
  sed -i '' "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated REDIS_PASSWORD"
fi

if need "PUSHER_APP_SECRET"; then
  sed -i '' "s/^PUSHER_APP_SECRET=.*/PUSHER_APP_SECRET=$(openssl rand -hex 16)/" .env
  echo "  Generated PUSHER_APP_SECRET"
fi

echo "Secrets ready."
