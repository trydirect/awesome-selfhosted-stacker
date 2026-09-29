#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  cp .env.example .env
fi
echo "Secrets ready. (No secrets needed for Speedtest Tracker)"
if ! grep -q "^APP_KEY=." .env 2>/dev/null; then
  val="base64:$(openssl rand -base64 32)"
  if grep -q "^APP_KEY=" .env; then
    sed -i '' "s|^APP_KEY=.*|APP_KEY=${val}|" .env
  else
    echo "APP_KEY=${val}" >> .env
  fi
  echo "  Generated APP_KEY"
fi
echo "Secrets ready."
