#!/bin/bash
set -e

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating $ENV_FILE from .env.example..."
  cp .env.example "$ENV_FILE"
fi

need() {
  if grep -q "^$1=" "$ENV_FILE" 2>/dev/null; then
    val=$(grep "^$1=" "$ENV_FILE" | head -1 | cut -d'=' -f2-)
    if [ -z "$val" ]; then
      val=$(eval "$2")
      sed -i '' "s|^$1=.*|$1=${val}|" "$ENV_FILE"
      echo "Generated $1"
    fi
  else
    val=$(eval "$2")
    echo "$1=${val}" >> "$ENV_FILE"
    echo "Generated $1"
  fi
}

need "ENCRYPTION_KEY" "openssl rand -hex 32"
need "JWT_SECRET" "openssl rand -hex 32"

echo "Secrets ready in $ENV_FILE"
