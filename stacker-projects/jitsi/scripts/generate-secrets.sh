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

if need "DB_PASSWORD"; then
  sed_inplace "s/^DB_PASSWORD=.*/DB_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated DB_PASSWORD"
fi

if need "ADMIN_PASSWORD"; then
  sed_inplace "s/^ADMIN_PASSWORD=.*/ADMIN_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated ADMIN_PASSWORD"
fi

if need "SECRET_KEY"; then
  sed_inplace "s/^SECRET_KEY=.*/SECRET_KEY=$(openssl rand -hex 32)/" .env
  echo "  Generated SECRET_KEY"
fi

if need "JWT_SECRET"; then
  sed_inplace "s/^JWT_SECRET=.*/JWT_SECRET=$(openssl rand -hex 32)/" .env
  echo "  Generated JWT_SECRET"
fi

if need "SMTP_PASSWORD"; then
  sed_inplace "s/^SMTP_PASSWORD=.*/SMTP_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated SMTP_PASSWORD"
fi

if need "SECRET_KEY_BASE"; then
  sed_inplace "s/^SECRET_KEY_BASE=.*/SECRET_KEY_BASE=$(openssl rand -hex 64)/" .env
  echo "  Generated SECRET_KEY_BASE"
fi

if need "OTP_SECRET"; then
  sed_inplace "s|^OTP_SECRET=.*|OTP_SECRET=$(openssl rand -base64 32)|" .env
  echo "  Generated OTP_SECRET"
fi

if need "INTERNAL_TOKEN"; then
  sed_inplace "s/^INTERNAL_TOKEN=.*/INTERNAL_TOKEN=$(openssl rand -hex 32)/" .env
  echo "  Generated INTERNAL_TOKEN"
fi

if need "JICOFO_SECRET"; then
  sed_inplace "s/^JICOFO_SECRET=.*/JICOFO_SECRET=$(openssl rand -hex 16)/" .env
  echo "  Generated JICOFO_SECRET"
fi

if need "JVB_PASSWORD"; then
  sed_inplace "s/^JVB_PASSWORD=.*/JVB_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated JVB_PASSWORD"
fi

if need "JIGASI_PASSWORD"; then
  sed_inplace "s/^JIGASI_PASSWORD=.*/JIGASI_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated JIGASI_PASSWORD"
fi

if need "JIBRI_PASSWORD"; then
  sed_inplace "s/^JIBRI_PASSWORD=.*/JIBRI_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated JIBRI_PASSWORD"
fi

if need "JICOFO_PASSWORD"; then
  sed_inplace "s/^JICOFO_PASSWORD=.*/JICOFO_PASSWORD=$(openssl rand -hex 16)/" .env
  echo "  Generated JICOFO_PASSWORD"
fi

if need "ADMIN_TOKEN"; then
  sed_inplace "s/^ADMIN_TOKEN=.*/ADMIN_TOKEN=$(openssl rand -hex 32)/" .env
  echo "  Generated ADMIN_TOKEN"
fi

echo "Secrets ready."
