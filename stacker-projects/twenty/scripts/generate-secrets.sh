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
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "DB_PASSWORD"; then
  val=$(openssl rand -hex 16)
  if grep -q "^DB_PASSWORD=" .env; then sed_inplace "s|^DB_PASSWORD=.*|DB_PASSWORD=${val}|" .env; else echo "DB_PASSWORD=${val}" >> .env; fi
  echo "  Generated DB_PASSWORD"
fi
if need "ENCRYPTION_KEY"; then
  val=$(openssl rand -hex 16)
  if grep -q "^ENCRYPTION_KEY=" .env; then sed_inplace "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=${val}|" .env; else echo "ENCRYPTION_KEY=${val}" >> .env; fi
  echo "  Generated ENCRYPTION_KEY"
fi
echo "Secrets ready."
