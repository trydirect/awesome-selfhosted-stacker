#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  cp .env.example .env
fi
need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}
if need "MINIO_ROOT_USER"; then
  sed -i '' "s|^MINIO_ROOT_USER=.*|MINIO_ROOT_USER=minioadmin|" .env
  echo "  Set MINIO_ROOT_USER"
fi
if need "MINIO_ROOT_PASSWORD"; then
  sed -i '' "s|^MINIO_ROOT_PASSWORD=.*|MINIO_ROOT_PASSWORD=$(openssl rand -hex 16)|" .env
  echo "  Generated MINIO_ROOT_PASSWORD"
fi
echo "Secrets ready."
