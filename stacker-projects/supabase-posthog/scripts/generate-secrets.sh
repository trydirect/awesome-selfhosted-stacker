#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_DIR/.env"
ENV_EXAMPLE="$PROJECT_DIR/.env.example"
KONG_FILE="$PROJECT_DIR/kong.yml"

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
  local current
  current="$(grep "^${key}=" "$ENV_FILE" | cut -d= -f2-)"
  if [ -z "$current" ]; then
    sed -i '' "s|^${key}=$|${key}=${value}|" "$ENV_FILE"
    echo "  set ${key}"
  fi
}

echo "Filling empty secrets in $ENV_FILE..."

set_if_empty "POSTGRES_PASSWORD"   "$(openssl rand -hex 16)"
set_if_empty "JWT_SECRET"          "$(openssl rand -hex 32)"
set_if_empty "SECRET_KEY_BASE"     "$(openssl rand -hex 64)"
set_if_empty "PG_META_CRYPTO_KEY"  "$(openssl rand -hex 32)"
set_if_empty "DASHBOARD_PASSWORD"  "$(openssl rand -hex 16)"
set_if_empty "POSTHOG_DB_PASSWORD" "$(openssl rand -hex 16)"
set_if_empty "POSTHOG_SECRET_KEY"  "$(openssl rand -hex 32)"

# ANON_KEY and SERVICE_ROLE_KEY are JWT tokens signed with JWT_SECRET.
# For a self-hosted demo, random hex strings are sufficient for Kong to boot;
# replace with real tokens from the Supabase JWT tool for production use.
set_if_empty "ANON_KEY"           "$(openssl rand -hex 32)"
set_if_empty "SERVICE_ROLE_KEY"   "$(openssl rand -hex 32)"

set_if_empty "SMTP_PASS" ""

echo "Done."

# Regenerate kong.yml with the generated keys so Kong can authenticate requests.
ANON_KEY="$(grep "^ANON_KEY=" "$ENV_FILE" | cut -d= -f2-)"
SERVICE_ROLE_KEY="$(grep "^SERVICE_ROLE_KEY=" "$ENV_FILE" | cut -d= -f2-)"

cat > "$KONG_FILE" <<EOF
_format_version: "3.0"
_transform: true

services:
  - name: auth-v1
    url: http://auth:9999
    routes:
      - name: auth-all
        paths:
          - /auth/v1/
    plugins:
      - name: cors

  - name: rest-v1
    url: http://rest:3000
    routes:
      - name: rest-all
        paths:
          - /rest/v1/
    plugins:
      - name: cors

  - name: realtime-v1
    url: http://realtime:4000
    routes:
      - name: realtime-all
        paths:
          - /realtime/v1/
    plugins:
      - name: cors

  - name: storage-v1
    url: http://storage:5000
    routes:
      - name: storage-all
        paths:
          - /storage/v1/
    plugins:
      - name: cors

consumers:
  - username: anon
    keyauth_credentials:
      - key: ${ANON_KEY}
  - username: service_role
    keyauth_credentials:
      - key: ${SERVICE_ROLE_KEY}

plugins:
  - name: correlation-id
    config:
      header_name: X-Request-ID
      generator: uuid
      echo_downstream: true
EOF

echo "Regenerated ${KONG_FILE} with current API keys."
