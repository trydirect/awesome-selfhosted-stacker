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

# --- contract-key alignment (config_contract generated fields) ---
gen() { openssl rand -hex 16; }
sync() { # sync <KEY> <VALUE>
  if grep -q "^${1}=" .env; then sed -i '' "s|^${1}=.*|${1}=${2}|" .env; else echo "${1}=${2}" >> .env; fi
}
ANON=$(grep "^ANON_KEY=" .env | cut -d= -f2-)
SVC=$(grep "^SERVICE_ROLE_KEY=" .env | cut -d= -f2-)
JWT=$(grep "^JWT_SECRET=" .env | cut -d= -f2-)
PG=$(grep "^POSTGRES_PASSWORD=" .env | cut -d= -f2-)
CRYPTO=$(grep "^PG_META_CRYPTO_KEY=" .env | cut -d= -f2-)
sync SUPABASE_ANON_KEY "$ANON"
sync SUPABASE_SERVICE_KEY "$SVC"
sync SUPABASE_SERVICE_ROLE_KEY "$SVC"
sync SERVICE_KEY "$SVC"
sync DB_PASSWORD "$PG"
sync GOTRUE_JWT_SECRET "$JWT"
sync PGRST_JWT_SECRET "$JWT"
sync PGRST_APP_SETTINGS_JWT_SECRET "$JWT"
sync CRYPTO_KEY "$CRYPTO"
# The template's design: every role password equals POSTGRES_PASSWORD
sync AUTHENTICATOR_PASSWORD "$PG"
sync SUPABASE_AUTH_ADMIN_PASSWORD "$PG"
sync SUPABASE_FUNCTIONS_ADMIN_PASSWORD "$PG"
sync DB_PASSWORD "$PG"
sync PG_META_DB_PASSWORD "$PG"
for key in SMTP_PASS METRICS_JWT_SECRET; do
  if ! grep -q "^${key}=." .env 2>/dev/null; then sync "${key}" "$(gen)"; fi
done
echo "  Contract keys aligned"

# postgresql.schema.sql: sets role passwords post-init (image reads /etc/postgresql.schema.sql)
{
  echo "ALTER ROLE authenticator PASSWORD '$(grep "^AUTHENTICATOR_PASSWORD=" .env | cut -d= -f2-)';"
  echo "ALTER ROLE supabase_auth_admin PASSWORD '$(grep "^SUPABASE_AUTH_ADMIN_PASSWORD=" .env | cut -d= -f2-)';"
  echo "ALTER ROLE supabase_functions_admin PASSWORD '$(grep "^SUPABASE_FUNCTIONS_ADMIN_PASSWORD=" .env | cut -d= -f2-)';"
  echo "ALTER ROLE supabase_storage_admin PASSWORD '$(grep "^SUPABASE_AUTH_ADMIN_PASSWORD=" .env | cut -d= -f2-)';"
  echo "ALTER ROLE supabase_read_only_user PASSWORD '$(grep "^AUTHENTICATOR_PASSWORD=" .env | cut -d= -f2-)';"
  echo "CREATE SCHEMA IF NOT EXISTS graphql_public;"
  echo "DO \$\$ DECLARE r RECORD; BEGIN FOR r IN SELECT proname, pg_get_function_identity_arguments(oid) AS args FROM pg_proc WHERE pronamespace = 'auth'::regnamespace LOOP EXECUTE format('ALTER FUNCTION auth.%I(%s) OWNER TO supabase_auth_admin', r.proname, r.args); END LOOP; END \$\$;"
  echo "ALTER SCHEMA auth OWNER TO supabase_auth_admin;"
} > postgresql.schema.sql
echo "  Wrote postgresql.schema.sql"
if ! grep -q "^DB_ENC_KEY=." .env 2>/dev/null; then sync DB_ENC_KEY "$(openssl rand -hex 8)"; fi
echo "  DB_ENC_KEY (16-byte AES-128) set"
