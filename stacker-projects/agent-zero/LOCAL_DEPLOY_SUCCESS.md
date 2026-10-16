# agent-zero — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `agent0ai/agent-zero:v2.14`, port 50080→80)

## Commands

```bash
cd stacker-projects/agent-zero
./scripts/generate-secrets.sh     # .env from .env.example, AUTH_LOGIN + AUTH_PASSWORD
stacker deploy --target local
```

## Verification

- `docker ps` → `agent-zero-app-1 Up (healthy) 0.0.0.0:50080->80/tcp`
- `curl -I http://localhost:50080/` → `HTTP/1.1 302 Found` (uvicorn, redirect
  to auth) — app + basic auth working as configured.

## Notes

- Container became healthy within the first healthcheck pass (start_period 60s).
- Teardown: `stacker destroy -y`; project image removed afterwards
  (`docker rmi agent0ai/agent-zero:v2.14`).
