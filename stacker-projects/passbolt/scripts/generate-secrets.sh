#!/bin/bash
set -euo pipefail

# generate-secrets.sh — generate random secrets for Passbolt

generate_if_empty() {
  local var_name="$1"
  local length="${2:-32}"
  if grep -q "^${var_name}=" .env 2>/dev/null; then
    local current_value
    current_value=$(grep "^${var_name}=" .env | cut -d'=' -f2-)
    if [ -n "$current_value" ] && [ "$current_value" != "changeme" ]; then
      echo "[INFO] ${var_name} already set, skipping."
      return
    fi
  fi
  local new_value
  new_value=$(openssl rand -base64 "$length" | tr -d '/+=' | head -c "$length")
  if grep -q "^${var_name}=" .env 2>/dev/null; then
    sed -i.bak "s|^${var_name}=.*|${var_name}=${new_value}|" .env && rm -f .env.bak
  else
    echo "${var_name}=${new_value}" >> .env
  fi
  echo "[GENERATED] ${var_name}=${new_value}"
}

if [ ! -f .env ]; then
  if [ -f .env.example ]; then
    cp .env.example .env
    echo "[INFO] Created .env from .env.example"
  else
    touch .env
    echo "[INFO] Created empty .env"
  fi
fi

generate_if_empty PASSBOLT_DATABASE_PASSWORD 24

echo "[DONE] Secrets generated."
echo "[NOTE] PASSBOLT_GPG_KEY_FINGERPRINT must be set manually after generating GPG keys."
