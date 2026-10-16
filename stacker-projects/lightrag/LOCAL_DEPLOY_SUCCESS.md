# lightrag — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `ghcr.io/hkuds/lightrag:v1.5.7`, port 9621,
postgres:16-alpine + qdrant)

## Commands

```bash
cd stacker-projects/lightrag
./scripts/generate-secrets.sh     # POSTGRES_PASSWORD + LLM/embedding config
stacker deploy --target local
```

## Verification

- `docker ps` → `lightrag-app-1 Up (healthy) :9621`, `lightrag-postgres-1 Up
  (healthy)`, `lightrag-qdrant-1 Up (healthy)`
- `curl http://localhost:9621/health` → `{"status":"healthy",...
  "core_version":"1.5.7","webui_available":true, ...}` with storage config
  `kv_storage: PGKVStorage`, `vector_storage: QdrantVectorDBStorage`

## Notes

- LLM/embedding bindings configured via `.env` (openai-compatible endpoints);
  app starts without reachable LLM (needed only at query/ingest time).
- Teardown: `stacker destroy -y`; project images removed afterwards
  (`ghcr.io/hkuds/lightrag:v1.5.7`, `postgres:16-alpine`, `qdrant/...`).
