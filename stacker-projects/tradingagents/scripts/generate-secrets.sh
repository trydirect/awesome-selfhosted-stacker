#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; echo "  Created .env from .env.example"; fi
echo "Secrets ready. (No generated secrets needed for tradingagents — LLM keys are user-supplied)"
