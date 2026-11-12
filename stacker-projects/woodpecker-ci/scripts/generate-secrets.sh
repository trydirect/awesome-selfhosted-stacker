#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."

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
if [ ! -f .env ]; then
  cp .env.example .env
fi
need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}
if need "AGENT_SECRET"; then
  sed_inplace "s|^AGENT_SECRET=.*|AGENT_SECRET=$(openssl rand -hex 32)|" .env
  echo "  Generated AGENT_SECRET"
fi
if ! grep -q "^WOODPECKER_AGENT_SECRET=." .env 2>/dev/null; then
  val=$(grep "^AGENT_SECRET=" .env | cut -d= -f2-)
  [ -z "$val" ] && val=$(openssl rand -hex 16)
  if grep -q "^WOODPECKER_AGENT_SECRET=" .env; then
    sed_inplace "s|^WOODPECKER_AGENT_SECRET=.*|WOODPECKER_AGENT_SECRET=${val}|" .env
  else
    echo "WOODPECKER_AGENT_SECRET=${val}" >> .env
  fi
  echo "  Synced WOODPECKER_AGENT_SECRET"
fi
echo "Secrets ready."
