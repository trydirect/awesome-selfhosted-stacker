#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
EXAMPLE_FILE="$SCRIPT_DIR/../.env.example"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating .env from .env.example..."
  cp "$EXAMPLE_FILE" "$ENV_FILE"
fi

generate_if_empty() {
  local key="$1"
  local length="$2"

  current=$(grep "^${key}=" "$ENV_FILE" | cut -d'=' -f2- || true)
  if [ -z "$current" ]; then
    value=$(openssl rand -hex "$length")
    if grep -q "^${key}=" "$ENV_FILE"; then
      sed -i '' "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
      echo "${key}=${value}" >> "$ENV_FILE"
    fi
    echo "Generated ${key}"
  else
    echo "Skipping ${key} (already set)"
  fi
}

generate_if_empty DB_PASSWORD 16
generate_if_empty APP_SECRET 32

echo "Secrets generation complete."
