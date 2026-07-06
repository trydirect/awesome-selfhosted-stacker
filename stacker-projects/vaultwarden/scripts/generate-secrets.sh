#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="$(dirname "$0")/../.env"
ENV_EXAMPLE="$(dirname "$0")/../.env.example"

if [ ! -f "$ENV_FILE" ]; then
  echo "==> .env not found, copying from .env.example..."
  cp "$ENV_EXAMPLE" "$ENV_FILE"
fi

echo "==> Generating missing secrets..."

generate_if_empty() {
  local key="$1"
  local generator="$2"
  local current
  current="$(grep -E "^${key}=" "$ENV_FILE" | cut -d= -f2-)"
  if [ -z "$current" ]; then
    local new_val
    new_val="$(eval "$generator")"
    if grep -q "^${key}=" "$ENV_FILE"; then
      sed -i '' "s|^${key}=.*|${key}=${new_val}|" "$ENV_FILE"
    else
      echo "${key}=${new_val}" >> "$ENV_FILE"
    fi
    echo "  [OK] $key generated"
  else
    echo "  [SKIP] $key already set"
  fi
}

generate_if_empty "ADMIN_TOKEN" "openssl rand -base64 48"

echo "==> Secrets generation complete."
