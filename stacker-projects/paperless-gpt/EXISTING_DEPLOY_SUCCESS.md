# paperless-gpt — existing server deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), target: existing server 46.224.127.228 (2 vCPU / 2 GB)
**Template:** stacker.yml (icereed/paperless-gpt:v0.31.0 + paperless-ngx:3.3.1
+ postgres + redis)

## Commands

```bash
cd stacker-projects/paperless-gpt
./scripts/generate-secrets.sh
# .env: OPENAI_API_KEY=user-supplied (required at app startup; placeholder
# used here — real key needed for actual LLM features)
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
export DEPLOY_HOST=46.224.127.228
stacker deploy --target server
```

Deploy history: #1368 (app crash-loop: empty OPENAI_API_KEY baked into
compose), #1369 (env change did not propagate — cached `.stacker/` compose),
#1370 (fresh generation after `rm -rf .stacker`) — **completed**.

## Verification (from the server host; external ports firewalled)

- `docker ps` → all four `Up (healthy)`: `project-app-1` (paperless-gpt),
  `project-paperless-1` (paperless-ngx), `project-paperless_db-1`, `project-redis-1`
- `curl http://localhost:8080/api/version` →
  `{"buildDate":"...","commit":"49c425...","version":"v0.31.0"}`
- `curl http://localhost:8000/api/` → HTTP 302 (paperless-ngx login redirect)

## Notes

- Image tag fix applied earlier this day: `ghcr.io/paperless-ngx/paperless-ngx`
  tags have no `v` prefix (`v3.3.1` → `3.3.1`).
- `OPENAI_API_KEY` must be non-empty in `.env` before deploy — the app exits
  fatally otherwise (`.env.example` marks it user-supplied; nothing validates
  it pre-deploy — see BUGS.md).
- **stacker CLI gotcha:** redeploy does not regenerate
  `.stacker/docker-compose.yml`; env values baked at first generation persist
  until `.stacker/` is removed (logged to root BUGS.md).
- External access to 8000/8080 is blocked by the server's firewall — verified
  via SSH host curls (read-only). Opening the ports is an infra task.
- Server RAM (2 GB) is sufficient for this stack (all healthy).
- Teardown: `stacker destroy -y` after verification to free RAM for the next
  test (server compose project name is shared).
