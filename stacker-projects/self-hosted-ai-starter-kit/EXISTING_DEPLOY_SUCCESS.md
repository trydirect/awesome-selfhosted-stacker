# self-hosted-ai-starter-kit — existing server deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), target: existing server 46.224.127.228 (2 vCPU / 2 GB)
**Template:** stacker.yml (n8nio/n8n:2.43.6 + postgres:16-alpine +
ollama/ollama:0.40.5 + qdrant/qdrant:v1.19.2)

## Commands

```bash
cd stacker-projects/self-hosted-ai-starter-kit
./scripts/generate-secrets.sh
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
export DEPLOY_HOST=46.224.127.228
stacker deploy --target server
```

## Verification (from the server host; external ports firewalled)

- `docker compose -p project ps` → all four `Up (healthy)`:
  `project-app-1` (n8n :5678), `project-postgres-1`, `project-ollama-1`,
  `project-qdrant-1`
- `curl http://localhost:5678/healthz` → `{"status":"ok"}`
- `curl http://localhost:5678/` → HTTP 200

## Caveat (platform)

- Deployments #1372 and #1373 both ended `paused [internal_error]` per the
  Stacker platform **while the stack itself deployed and became healthy**
  (side services after #1372, the full stack including n8n after the retry).
  Platform false-negative — logged to project BUGS.md and root BUGS.md.

## Notes

- RAM: fits the 2 GB test server (ollama idle without models).
- Teardown after verification: server-side
  `docker compose -p project down --volumes` (stacker destroy is local-only).
