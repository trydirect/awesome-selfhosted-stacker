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

set_secret() {
  local key="$1" val="$2"
  if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s|^$key=.*|$key=$val|" .env
  else
    sed -i "s|^$key=.*|$key=$val|" .env
  fi
}

if need "GITLAB_ROOT_PASSWORD"; then
  set_secret "GITLAB_ROOT_PASSWORD" "$(openssl rand -hex 24)"
  echo "  Generated GITLAB_ROOT_PASSWORD"
fi

if need "SECRET_KEY_BASE"; then
  set_secret "SECRET_KEY_BASE" "$(openssl rand -hex 64)"
  echo "  Generated SECRET_KEY_BASE"
fi

if need "OTP_SECRET"; then
  set_secret "OTP_SECRET" "$(openssl rand -base64 32)"
  echo "  Generated OTP_SECRET"
fi

# Generate gitlab.rb from .env values
GITLAB_DOMAIN=$(grep "^GITLAB_DOMAIN=" .env | cut -d= -f2-)
GITLAB_ROOT_PASSWORD=$(grep "^GITLAB_ROOT_PASSWORD=" .env | cut -d= -f2-)

cat > gitlab.rb << EOF
external_url 'http://${GITLAB_DOMAIN}'
nginx['listen_port'] = 80
nginx['listen_https'] = false
gitlab_rails['gitlab_shell_ssh_port'] = 2222
gitlab_rails['initial_root_password'] = '${GITLAB_ROOT_PASSWORD}'
EOF
echo "  Generated gitlab.rb"

echo "Secrets ready."
