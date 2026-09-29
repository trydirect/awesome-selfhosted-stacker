#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/../.env"
EXAMPLE_FILE="$SCRIPT_DIR/../.env.example"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating .env from .env.example..."
  cp "$EXAMPLE_FILE" "$ENV_FILE"
fi

for key in STRAVA_CLIENT_SECRET STRAVA_REFRESH_TOKEN; do
  if ! grep -q "^${key}=." "$ENV_FILE" 2>/dev/null; then
    val=$(openssl rand -hex 16)
    if grep -q "^${key}=" "$ENV_FILE"; then
      sed -i '' "s|^${key}=.*|${key}=${val}|" "$ENV_FILE"
    else
      echo "${key}=${val}" >> "$ENV_FILE"
    fi
    echo "  Generated ${key} (contract-declared)"
  fi
done
echo "Secrets ready."
