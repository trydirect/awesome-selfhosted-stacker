#!/bin/bash
set -e

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating $ENV_FILE from .env.example..."
  cp .env.example "$ENV_FILE"
fi

echo "Dockhand uses SQLite by default - no secrets required."
echo "Environment ready in $ENV_FILE"
