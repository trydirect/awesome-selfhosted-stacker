# openagent — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `casbin/openagent:2.95.1`, port 14000,
mysql:8.0.43)

## Commands

```bash
cd stacker-projects/openagent
./scripts/generate-secrets.sh     # DB_PASSWORD
stacker deploy --target local
```

## Verification (after db image fix)

- `docker ps` → `openagent-app-1 Up (healthy) :14000`, `openagent-db-1 Up (healthy)`
- `curl http://localhost:14000/api/health` → `{"status":"ok",...}`

## Fix applied

- Original `mysql:8.0.25` has no arm64 manifest (pull failed on this host).
  Pinned `mysql:8.0.43` (multi-arch: amd64+arm64) — safe for x86_64 servers.
  See BUGS.md.

## Notes

- `command: "--createDatabase=true"` creates the Casibase/OpenAgent schema on
  first boot; `DOCKER_DB_HOST=db` + `RUNNING_IN_DOCKER=true` rewrite the DSN.
- Teardown: `stacker destroy -y`; project images removed afterwards
  (`casbin/openagent:2.95.1`, `mysql:8.0.43`).
