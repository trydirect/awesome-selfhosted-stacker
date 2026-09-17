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
if need "FRIGATE_RTSP_PASSWORD"; then
  sed -i '' "s|^FRIGATE_RTSP_PASSWORD=.*|FRIGATE_RTSP_PASSWORD=$(openssl rand -hex 12)|" .env
  echo "  Generated FRIGATE_RTSP_PASSWORD"
fi
echo "Secrets ready."
