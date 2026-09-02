#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"

# Idempotent: copy .env.example to .env if .env doesn't exist
if [ ! -f "$ENV_FILE" ]; then
  if [ ! -f "$ENV_EXAMPLE" ]; then
    echo "Error: $ENV_EXAMPLE not found" >&2
    exit 1
  fi
  cp "$ENV_EXAMPLE" "$ENV_FILE"
  echo "Created $ENV_FILE from $ENV_EXAMPLE"
fi

# Helper: set a key in .env only if currently empty
set_if_empty() {
  local key="$1"
  local value="$2"
  local comment="${3:-}"
  local current
  current="$(grep "^${key}=" "$ENV_FILE" | cut -d= -f2-)"
  if [ -z "$current" ]; then
    if [ -n "$comment" ]; then
      sed -i '' "s|^${key}=$|# ${comment}\n${key}=${value}|" "$ENV_FILE"
    else
      sed -i '' "s|^${key}=$|${key}=${value}|" "$ENV_FILE"
    fi
    echo "  set ${key}"
  fi
}

echo "Filling empty secrets in $ENV_FILE..."

set_if_empty "POSTGRES_PASSWORD"   "$(openssl rand -hex 16)"
set_if_empty "JWT_SECRET"          "$(openssl rand -hex 32)"
set_if_empty "SECRET_KEY_BASE"     "$(openssl rand -hex 64)"
set_if_empty "PG_META_CRYPTO_KEY"  "$(openssl rand -hex 32)"
set_if_empty "DASHBOARD_PASSWORD"  "$(openssl rand -hex 16)"

# ANON_KEY and SERVICE_ROLE_KEY are actually JWT tokens signed with JWT_SECRET.
# Generate a placeholder of appropriate length; replace with real tokens from
# the Supabase JWT tool: https://supabase.com/docs/guides/self-hosting/docker#generate-api-keys
set_if_empty "ANON_KEY"           "$(openssl rand -hex 32)" \
  "replace with real token: https://supabase.com/docs/guides/self-hosting/docker#generate-api-keys"
set_if_empty "SERVICE_ROLE_KEY"   "$(openssl rand -hex 32)" \
  "replace with real token: https://supabase.com/docs/guides/self-hosting/docker#generate-api-keys"

# SMTP_PASS must be provided by the user (real SMTP credentials)
set_if_empty "SMTP_PASS" "" \
  "provide your real SMTP password"

echo "Done."
