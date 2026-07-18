#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then
  cp .env.example .env
  echo "  Created .env from .env.example"
fi
echo "Secrets ready. (No secrets needed for Stirling-PDF)"
