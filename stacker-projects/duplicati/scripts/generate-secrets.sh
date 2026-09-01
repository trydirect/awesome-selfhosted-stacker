#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  cp .env.example .env
fi
if ! grep -q "^SETTINGS_ENCRYPTION_KEY=.\+" .env 2>/dev/null; then
  grep -q "^SETTINGS_ENCRYPTION_KEY=" .env 2>/dev/null \
    && sed -i.bak "s|^SETTINGS_ENCRYPTION_KEY=.*|SETTINGS_ENCRYPTION_KEY=$(openssl rand -hex 32)|" .env && rm -f .env.bak \
    || echo "SETTINGS_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env
  echo "Generated SETTINGS_ENCRYPTION_KEY"
fi
echo "Secrets ready."
