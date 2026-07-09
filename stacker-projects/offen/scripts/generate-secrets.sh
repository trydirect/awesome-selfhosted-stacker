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
  local mode="$2"
  local size="${3:-}"
  local current
  local value
  current=$(grep "^${key}=" "$ENV_FILE" | cut -d"=" -f2- || true)
  if [ -n "$current" ]; then
    echo "Skipping ${key} (already set)"
    return
  fi
  case "$mode" in
    hex)
      value=$(openssl rand -hex "$size")
      ;;
    base64)
      value=$(openssl rand -base64 "$size" | tr -d "\n")
      ;;
    uuid)
      value=$(uuidgen | tr "A-Z" "a-z")
      ;;
    laravel)
      value="base64:$(openssl rand -base64 32 | tr -d "\n")"
      ;;
    *)
      echo "Unknown generation mode: $mode" >&2
      exit 1
      ;;
  esac
  if grep -q "^${key}=" "$ENV_FILE"; then
    sed -i "" "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
  echo "Generated ${key}"
}

generate_if_empty OFFEN_SECRET base64 32
generate_if_empty OFFEN_APP_ROOTACCOUNT uuid

echo "Secrets generation complete."
