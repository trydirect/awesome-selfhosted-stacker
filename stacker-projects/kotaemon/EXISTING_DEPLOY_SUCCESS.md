# kotaemon — existing server deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), target: existing server 167.233.196.133 (cpx42)
**Template:** stacker.yml (Cinnamon/kotaemon `main-lite` single container, port 7860)

## Commands

```bash
cd stacker-projects/kotaemon
./scripts/generate-secrets.sh
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
export DEPLOY_HOST=167.233.196.133
stacker deploy --target server --server-host 167.233.196.133   # #1381
```

## Verification

- `docker ps` → `project-app-1 Up (healthy)` (single-container `main-lite`
  build — no Elasticsearch in this template)
- `curl http://localhost:7860/` → HTTP 200
- External `http://167.233.196.133:7860/` → HTTP 200 after
  `stacker cloud firewall add --public-ports 7860/tcp`
- RAM ~1.3 GiB for the whole host at idle — light stack

## Notes

- **Security caveat stands:** upstream RCE #844 / IDOR #846 — self-host only,
  never expose publicly, and do not submit to the marketplace until fixed
  (see BUGS.md).
- Teardown after verification: server-side
  `docker compose -p project down --volumes`.
