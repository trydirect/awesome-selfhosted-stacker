#!/bin/sh
# Fill every empty secret in .env, creating .env from .env.example first.
# Values already set are kept. Portable: macOS and Linux (no `sed -i`).
#
# The generators match config_contract in stacker.yml, which a Quick Deploy
# clone uses to generate fresh values on the buyer's machine.
set -eu
cd "$(dirname "$0")/.."

[ -f .env ] || { cp .env.example .env; echo "  Created .env from .env.example"; }

get() { grep "^$1=" .env 2>/dev/null | head -1 | cut -d= -f2- || true; }

set_value() {
  tmp=$(mktemp)
  awk -v k="$1" -v v="$2" 'BEGIN{done=0}
    index($0, k "=") == 1 && !done { print k "=" v; done=1; next } { print }
    END { if (!done) print k "=" v }' .env > "$tmp"
  cat "$tmp" > .env
  rm -f "$tmp"
}

alnum() { LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c "$1"; }
hex() { openssl rand -hex "$1"; }

fill() {
  [ -n "$(get "$1")" ] && return 0
  set_value "$1" "$2"
  echo "  Generated $1"
}

b64url() { openssl base64 -A | tr '+/' '-_' | tr -d '='; }

# HS256 JWT signed with JWT_SECRET (Supabase's legacy API keys).
jwt() {
  header=$(printf '{"alg":"HS256","typ":"JWT"}' | b64url)
  payload=$(printf '%s' "$1" | b64url)
  sig=$(printf '%s.%s' "$header" "$payload" \
    | openssl dgst -sha256 -hmac "$(get JWT_SECRET)" -binary | b64url)
  printf '%s.%s.%s' "$header" "$payload" "$sig"
}

fill POSTGRES_PASSWORD "$(alnum 32)"
fill JWT_SECRET "$(alnum 40)"
fill DASHBOARD_PASSWORD "$(alnum 32)"
fill SECRET_KEY_BASE "$(hex 32)"
fill REALTIME_DB_ENC_KEY "$(alnum 16)"
fill VAULT_ENC_KEY "$(alnum 32)"
fill PG_META_CRYPTO_KEY "$(alnum 32)"
fill S3_PROTOCOL_ACCESS_KEY_ID "$(hex 16)"
fill S3_PROTOCOL_ACCESS_KEY_SECRET "$(hex 32)"
fill N8N_ENCRYPTION_KEY "$(alnum 32)"
fill N8N_USER_MANAGEMENT_JWT_SECRET "$(alnum 32)"
fill WEBUI_SECRET_KEY "$(alnum 32)"
fill FLOWISE_PASSWORD "$(alnum 32)"
fill NEO4J_PASSWORD "$(alnum 32)"
fill CLICKHOUSE_PASSWORD "$(alnum 32)"
fill MINIO_ROOT_USER "$(alnum 16)"
fill MINIO_ROOT_PASSWORD "$(alnum 32)"
fill LANGFUSE_SALT "$(alnum 32)"
fill LANGFUSE_ENCRYPTION_KEY "$(hex 32)"
fill LANGFUSE_POSTGRES_PASSWORD "$(alnum 32)"
fill NEXTAUTH_SECRET "$(alnum 32)"
fill REDIS_AUTH "$(alnum 32)"
fill SEARXNG_SECRET "$(alnum 32)"

# Claims match config_contract (derived_jwt) in stacker.yml.
fill ANON_KEY "$(jwt '{"exp":1918252800,"iat":1760486400,"iss":"supabase","role":"anon"}')"
fill SERVICE_ROLE_KEY "$(jwt '{"exp":1918252800,"iat":1760486400,"iss":"supabase","role":"service_role"}')"

echo "Secrets ready."
