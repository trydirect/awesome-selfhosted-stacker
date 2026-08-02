#!/usr/bin/env bash
set -euo pipefail

OLLAMA_URL="${OLLAMA_BASE_URL:-http://localhost:11434}"
MODEL="${1:-llama3.1}"
EMBED_MODEL="${2:-nomic-embed-text}"

echo "==> Waiting for Ollama to be ready..."
until curl -sf "$OLLAMA_URL/api/tags" > /dev/null 2>&1; do
  sleep 2
done
echo "  Ollama is ready."

echo "==> Pulling LLM model: $MODEL..."
curl -sf "$OLLAMA_URL/api/pull" -d "{\"name\":\"$MODEL\"}" --max-time 600
echo "  Model $MODEL pulled."

echo "==> Pulling embedding model: $EMBED_MODEL..."
curl -sf "$OLLAMA_URL/api/pull" -d "{\"name\":\"$EMBED_MODEL\"}" --max-time 300
echo "  Model $EMBED_MODEL pulled."

echo "==> All models ready."
