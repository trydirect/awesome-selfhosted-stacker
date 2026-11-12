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

ENV_FILE="${1:-.env}"

if [ ! -f "$ENV_FILE" ]; then
  echo "Creating $ENV_FILE from .env.example..."
  cp .env.example "$ENV_FILE"
fi

need() {
  if grep -q "^$1=" "$ENV_FILE" 2>/dev/null; then
    val=$(grep "^$1=" "$ENV_FILE" | head -1 | cut -d'=' -f2-)
    if [ -z "$val" ]; then
      val=$(eval "$2")
      sed_inplace "s|^$1=.*|$1=${val}|" "$ENV_FILE"
      echo "Generated $1"
    fi
  else
    val=$(eval "$2")
    echo "$1=${val}" >> "$ENV_FILE"
    echo "Generated $1"
  fi
}

need "ENCRYPTION_KEY" "openssl rand -hex 32"
need "JWT_SECRET" "openssl rand -hex 32"

echo "Secrets ready in $ENV_FILE"
