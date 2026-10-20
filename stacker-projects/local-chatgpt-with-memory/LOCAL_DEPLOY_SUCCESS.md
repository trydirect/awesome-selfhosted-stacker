# local-chatgpt-with-memory — local deploy success

**Date:** 2026-10-20
**Stacker:** 0.3.4, Docker (macOS), target: local
**Template:** stacker.yml (built from pinned upstream commit + qdrant + ollama, port 8501)

## Commands

```bash
cd stacker-projects/local-chatgpt-with-memory
./scripts/generate-secrets.sh
stacker deploy --target local
```

## Verification

- `docker ps` → `local-chatgpt-with-memory-app-1 Up (healthy)`,
  `...-qdrant-1 Up (healthy)`, `...-ollama-1 Up`
- `curl http://localhost:8501/` → HTTP 200 (Streamlit chat UI)

## Notes

- The upstream config hardcodes `localhost` for qdrant/ollama; the template
  Dockerfile rewrites them to the compose service names (`qdrant`,
  `ollama`).
- Models (llama3.1, nomic-embed-text) are pulled by ollama on first use —
  the first chat is slow because of the download.
- Teardown after verification: `stacker destroy -y`; project images removed
  afterwards (local image cleanup rule).
