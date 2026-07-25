#!/bin/bash
set -e
ENV_FILE=".env"

generate_if_empty() {
  local key="$1"
  local value
  value=$(openssl rand -hex 32)
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    local existing
    existing=$(grep "^${key}=" "$ENV_FILE" | cut -d'=' -f2-)
    if [ -n "$existing" ] && [ "$existing" != "" ]; then
      return
    fi
  fi
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    sed -i '' "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
  else
    echo "${key}=${value}" >> "$ENV_FILE"
  fi
  echo "Generated: ${key}"
}

generate_if_empty "JWT_SECRET"
generate_if_empty "DB_PASSWORD"
generate_if_empty "SECRET_KEY"
generate_if_empty "SECRET_KEY_BASE"
generate_if_empty "SESSION_SECRET"
generate_if_empty "APP_SECRET"
generate_if_empty "NEXTAUTH_SECRET"
generate_if_empty "ADMIN_PASSWORD"
