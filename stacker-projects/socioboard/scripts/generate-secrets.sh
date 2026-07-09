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

generate_if_empty AUTH_SECRET hex 32
generate_if_empty AUTH_TOKEN_SECRET hex 32
generate_if_empty SQL_DB_PASS hex 16
generate_if_empty SQL_DB_ROOT_PASS hex 16
generate_if_empty MONGO_PASS hex 16
generate_if_empty LARAVEL_KEY laravel
generate_if_empty ADMIN_PASSWORD hex 16
generate_if_empty ADMIN_SESSION_KEY hex 32
generate_if_empty API_SESSION_KEY_1 hex 32
generate_if_empty API_SESSION_KEY_2 hex 32

MONGO_USER=$(grep '^MONGO_USER=' "$ENV_FILE" | cut -d'=' -f2- || true)
MONGO_PASS=$(grep '^MONGO_PASS=' "$ENV_FILE" | cut -d'=' -f2- || true)
MONGO_DB_NAME=$(grep '^MONGO_DB_NAME=' "$ENV_FILE" | cut -d'=' -f2- || true)
cat > "$SCRIPT_DIR/../init-mongo.js" <<EOF
 db.createUser(
   {
     user: "$MONGO_USER",
     pwd: "$MONGO_PASS",
     roles: [ { role: "readWrite", db: "$MONGO_DB_NAME" } ]
   }
 )
 exit
EOF
echo "Rendered init-mongo.js"

echo "Secrets generation complete."
