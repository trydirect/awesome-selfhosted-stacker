#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
need() { [ -z "$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)" ]; }
if need "DB_PASSWORD"; then
  val=$(openssl rand -hex 16)
  if grep -q "^DB_PASSWORD=" .env; then sed -i '' "s|^DB_PASSWORD=.*|DB_PASSWORD=${val}|" .env; else echo "DB_PASSWORD=${val}" >> .env; fi
  echo "  Generated DB_PASSWORD"
fi
if need "ADMIN_PASSWORD"; then
  val="Fr33sc!ut.$(openssl rand -hex 6)"
  if grep -q "^ADMIN_PASSWORD=" .env; then sed -i '' "s|^ADMIN_PASSWORD=.*|ADMIN_PASSWORD=${val}|" .env; else echo "ADMIN_PASSWORD=${val}" >> .env; fi
  echo "  Generated ADMIN_PASSWORD"
fi
if need "ADMIN_EMAIL"; then
  val="admin@localhost.local"
  if grep -q "^ADMIN_EMAIL=" .env; then sed -i '' "s|^ADMIN_EMAIL=.*|ADMIN_EMAIL=${val}|" .env; else echo "ADMIN_EMAIL=${val}" >> .env; fi
  echo "  Set ADMIN_EMAIL"
fi
if need "ROOT_PASSWORD"; then
  val=$(openssl rand -hex 16)
  if grep -q "^ROOT_PASSWORD=" .env; then sed -i '' "s|^ROOT_PASSWORD=.*|ROOT_PASSWORD=${val}|" .env; else echo "ROOT_PASSWORD=${val}" >> .env; fi
  echo "  Generated ROOT_PASSWORD"
fi
echo "Secrets ready."
