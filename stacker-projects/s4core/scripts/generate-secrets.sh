#!/bin/bash
set -euo pipefail

# Generate initial S4 credentials without overwriting existing values.

readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly ENV_FILE="${SCRIPT_DIR}/../.env"
readonly EXAMPLE_FILE="${SCRIPT_DIR}/../.env.example"

if [[ ! -f "$ENV_FILE" ]]; then
  cp "$EXAMPLE_FILE" "$ENV_FILE"
  echo "Created .env from .env.example"
fi

need() {
  local key="$1"
  local val
  val=$(grep "^${key}=" "$ENV_FILE" 2>/dev/null | cut -d'=' -f2- || true)
  [[ -z "$val" ]]
}

set_env_value() {
  local key="$1"
  local value="$2"

  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i '' "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
}

if need "S4_ROOT_PASSWORD"; then
  set_env_value "S4_ROOT_PASSWORD" "$(openssl rand -hex 16)"
  echo "Generated S4_ROOT_PASSWORD"
fi

if need "S4_ACCESS_KEY_ID"; then
  set_env_value "S4_ACCESS_KEY_ID" "$(openssl rand -hex 12)"
  echo "Generated S4_ACCESS_KEY_ID"
fi

if need "S4_SECRET_ACCESS_KEY"; then
  set_env_value "S4_SECRET_ACCESS_KEY" "$(openssl rand -hex 32)"
  echo "Generated S4_SECRET_ACCESS_KEY"
fi

echo "Secrets ready."
