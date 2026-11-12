#!/bin/bash
set -e

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
    sed_inplace "s|^${key}=.*|${key}=${value}|" "$ENV_FILE"
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
