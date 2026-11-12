#!/usr/bin/env bash
set -euo pipefail

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
      sed_inplace "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
    else
      echo "${key}=${value}" >> "$ENV_FILE"
    fi
    echo "Generated ${key}"
  else
    echo "Skipping ${key} (already set)"
  fi
}

generate_if_empty ADMIN_PASSWORD 16

echo "Secrets generation complete."
