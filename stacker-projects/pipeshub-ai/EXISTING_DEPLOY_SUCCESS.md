# pipeshub-ai — existing server deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), target: existing server 167.233.196.133 (cpx42)
**Template:** stacker.yml (slim subset: app + mongodb + redis + qdrant + neo4j)

## Commands

```bash
cd stacker-projects/pipeshub-ai
./scripts/generate-secrets.sh
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
export DEPLOY_HOST=167.233.196.133
stacker deploy --target server --server-host 167.233.196.133   # #1380
```

## Verification

- `docker ps` → all five containers Up: `project-app-1 (healthy)`,
  `project-mongodb-1 (healthy)`, `project-redis-1 (healthy)`,
  `project-qdrant-1 (healthy)`, `project-neo4j-1 (healthy)`
- `curl http://localhost:3000/` → HTTP 200
- External `http://167.233.196.133:3000/` → HTTP 200 after
  `stacker cloud firewall add --public-ports 3000/tcp`
- App healthcheck (`/api/v1/health/services` grep for healthy) passes after
  its 300s start window — early checks fail while the data services warm up

## Notes

- RAM ~4.6 GiB with all five services (neo4j + mongo are the heavy ones) —
  confirms the ≥6 GB floor noted in BUGS.md; fits cpx42 (16 GB) comfortably,
  would not fit the 2 GB shared test server.
- Teardown between tests: server-side
  `docker compose -p project down --volumes`.
