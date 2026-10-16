# evolution-api — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `evoapicloud/evolution-api:v2.3.7`, port 8080,
postgres:15-alpine + redis:7-alpine)

## Commands

```bash
cd stacker-projects/evolution-api
./scripts/generate-secrets.sh     # DB_PASSWORD, AUTHENTICATION_API_KEY
stacker deploy --target local
```

## Verification

- `docker ps` → `evolution-api-app-1 Up (healthy) :8080`,
  `evolution-api-postgres-1 Up (healthy)`, `evolution-api-redis-1 Up (healthy)`
- `curl http://localhost:8080/` → HTTP 200
- `curl -H "apikey: $AUTHENTICATION_API_KEY" http://localhost:8080/instance/fetchInstances`
  → HTTP 200 (auth works)

## Notes

- CLI printed the known `✗ Timeout waiting for containers` false-negative
  (root BUGS.md:1063) — actual health reached within first check window.
- Teardown: `stacker destroy -y`; project images removed afterwards
  (`evoapicloud/evolution-api:v2.3.7`, `postgres:15-alpine`, `redis:7-alpine`).
