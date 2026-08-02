#!/usr/bin/env bash
set -euo pipefail

STACKPILOT_URL="${1:-http://localhost:8080}"

if [ $# -lt 1 ]; then
  echo "Usage: $0 <stackpilot_url> [website_url]"
  echo "  Example: $0 http://localhost:8080 https://example.com"
  exit 1
fi

WEBSITE_URL="${2:-}"

if [ -z "$WEBSITE_URL" ]; then
  echo "==> No website URL provided. Add documents manually via the dashboard."
  echo "    Dashboard: $STACKPILOT_URL/api/admin/dashboard"
  exit 0
fi

echo "==> Crawling $WEBSITE_URL..."
RESP=$(curl -sf -X POST "$STACKPILOT_URL/api/admin/websites/crawl" \
  -H "Content-Type: application/json" \
  -d "{\"url\":\"$WEBSITE_URL\",\"max_pages\":50}")

echo "  Result: $RESP"
echo "==> Knowledge base seeded."
