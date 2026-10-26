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

## Auth re-check (2026-10-26)

Upstream runs with no authentication unless `LIGHTRAG_API_KEY` or `AUTH_ACCOUNTS`
is set, and port 9621 is public. The stack now sets both (admin login, API key,
JWT secret, all generated) and `WHITELIST_PATHS=/health`, so the Ollama-compatible
`/api/*` routes are protected too. Fresh volumes, `stacker deploy --target local`:

| Request | Code |
|---|---|
| `GET /health`, no auth | 200 |
| `POST /query`, no auth | 401 |
| `POST /api/chat`, no auth | 401 |
| `GET /graph/label/list`, wrong `X-API-Key` | 401 |
| `GET /graph/label/list`, generated `X-API-Key` | 200 |
| `POST /login` admin, wrong password | 401 |
| `POST /login` admin, generated password, then JWT on `/graph/label/list` | 200 |
| `GET /auth-status` | `auth_configured: true` |
