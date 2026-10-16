# localagi — existing server deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), target: existing server 167.233.196.133 (cpx42)
**Template:** stacker.yml (quay.io/mudler/localagi:latest + localai v2.29.0 +
localrecall postgres)

## Commands

```bash
cd stacker-projects/localagi
./scripts/generate-secrets.sh
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
export DEPLOY_HOST=167.233.196.133
stacker deploy --target server --server-host 167.233.196.133
```

Deploy history: #1378 (broken `main-20261005225430` image — `serve` help
restart loop), #1379 after switching to `latest` + `LOCALAGI_MODEL` —
**completed**.

## Verification

- `docker ps` → `project-app-1 Up (healthy)`, `project-localai-1 Up`,
  `project-postgres-1 Up (healthy)`
- `curl http://localhost:8080/` → HTTP 302 (LocalAGI UI redirect);
  external `http://167.233.196.133:8080/` → 302 (port 8080 already in the
  server firewall from the first deploy)
- LocalAI sidecar: `curl http://localhost:8080/readyz` (inside
  `project-localai-1`) → `OK` — `gemma-3-4b-it-qat` +
  `granite-embedding-107m-multilingual` preloaded by its command

## Notes

- Image/env fix details in BUGS.md (broken rolling `main-*` builds;
  `LOCALAGI_MODEL` is mandatory).
- RAM ~1.8 GiB idle on cpx42 with models loaded — fits 16 GB comfortably.
- Teardown between tests: server-side
  `docker compose -p project down --volumes`.
