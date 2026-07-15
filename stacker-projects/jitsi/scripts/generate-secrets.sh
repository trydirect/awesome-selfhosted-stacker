#!/bin/bash
set -euo pipefail

# Generate secrets for first deploy. Fills empty values in .env,
# skips if already populated (re-deploys keep existing secrets).

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

if need "DB_PASSWORD"; then
  sed -i '' "s/^DB_PASSWORD=.*/DB_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated DB_PASSWORD"
fi

if need "ADMIN_PASSWORD"; then
  sed -i '' "s/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated ADMIN_PASSWORD"
fi

if need "SECRET_KEY"; then
  sed -i '' "s/^SECRET_KEY=.*/SECRET_KEY=$(openssl rand -hex 32)/" .env
  echo "  Generated SECRET_KEY"
fi

if need "JWT_SECRET"; then
  sed -i '' "s/^JWT_SECRET=.*/JWT_SECRET=$(openssl rand -hex 32)/" .env
  echo "  Generated JWT_SECRET"
fi

if need "SMTP_PASSWORD"; then
  sed -i '' "s/^SMTP_PASSWORD=.*/SMTP_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated SMTP_PASSWORD"
fi

if need "SECRET_KEY_BASE"; then
  sed -i '' "s/^SECRET_KEY_BASE=.*/SECRET_KEY_BASE=$(openssl rand -hex 64)/" .env
  echo "  Generated SECRET_KEY_BASE"
fi

if need "OTP_SECRET"; then
  sed -i '' "s|^OTP_SECRET=.*|OTP_SECRET=$(openssl rand -base64 32)|" .env
  echo "  Generated OTP_SECRET"
fi

if need "INTERNAL_TOKEN"; then
  sed -i '' "s/^INTERNAL_TOKEN=.*/INTERNAL_TOKEN=$(openssl rand -hex 32)/" .env
  echo "  Generated INTERNAL_TOKEN"
fi

if need "JICOFO_SECRET"; then
  sed -i '' "s/^JICOFO_SECRET=.*/JICOFO_SECRET=$(openssl rand -hex 16)/" .env
  echo "  Generated JICOFO_SECRET"
fi

if need "JVB_PASSWORD"; then
  sed -i '' "s/^JVB_PASSWORD=.*/JVB_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated JVB_PASSWORD"
fi

if need "JIGASI_PASSWORD"; then
  sed -i '' "s/^JIGASI_PASSWORD=.*/JIGASI_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated JIGASI_PASSWORD"
fi

if need "JIBRI_PASSWORD"; then
  sed -i '' "s/^JIBRI_PASSWORD=.*/JIBRI_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated JIBRI_PASSWORD"
fi

if need "JICOFO_PASSWORD"; then
  sed -i '' "s/^JICOFO_PASSWORD=.*/JICOFO_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated JICOFO_PASSWORD"
fi

if need "ADMIN_TOKEN"; then
  sed -i '' "s/^ADMIN_TOKEN=.*/ADMIN_TOKEN=$(openssl rand -hex 32)/" .env
  echo "  Generated ADMIN_TOKEN"
fi

echo "Secrets ready."
