# mautic — existing server deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), target: existing server 46.224.127.228 (2 vCPU / 2 GB)
**Template:** stacker.yml (mautic/mautic:6.0.6-apache web+worker+cron + mysql:lts)

## Commands

```bash
cd stacker-projects/mautic
./scripts/generate-secrets.sh
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
export DEPLOY_HOST=46.224.127.228
stacker deploy --target server     # deployment #1371
```

## Verification (from the server host; external ports firewalled)

- `docker ps` → `project-app-1 Up (healthy)`, `project-db-1 Up (healthy)`,
  `project-worker-1 Up`, `project-cron-1 Up` (all four roles)
- `curl http://localhost:8080/` → HTTP 302 → Mautic first-run **Install**
  wizard (expected on a fresh install)

## Notes

- Three app containers share one image via `DOCKER_MAUTIC_ROLE`
  (web / worker / cron) — the intended Mautic 6 deployment shape.
- RAM: fits the 2 GB test server (healthy with ~700 MB to spare after prune).
- Teardown after verification: server-side
  `docker compose -p project down --volumes` (the command stacker destroy
  prints — `stacker destroy` is local-only).
