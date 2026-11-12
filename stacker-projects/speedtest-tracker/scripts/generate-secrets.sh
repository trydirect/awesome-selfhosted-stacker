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
echo "Secrets ready. (No secrets needed for Speedtest Tracker)"
if ! grep -q "^APP_KEY=." .env 2>/dev/null; then
  val="base64:$(openssl rand -base64 32)"
  if grep -q "^APP_KEY=" .env; then
    sed_inplace "s|^APP_KEY=.*|APP_KEY=${val}|" .env
  else
    echo "APP_KEY=${val}" >> .env
  fi
  echo "  Generated APP_KEY"
fi
echo "Secrets ready."
