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
      sed_inplace "s|^${key}=.*|${key}=${new_val}|" "$ENV_FILE"
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
