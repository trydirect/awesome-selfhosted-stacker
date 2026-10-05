# AstrBot — Local Deploy Success

**Date:** 2026-10-04
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (2373565)

## Verification

| Check | Result |
|---|---|
| Containers | `astrbot-app-1` Up |
| HTTP `GET /` (6185) | **200** (WebUI HTML, zh-CN) |
| Port 6199 | published by template but nothing listens (optional panel port, not started by default) — non-blocking |

Note: deploy printed `✗ Timeout waiting for containers` (no healthcheck in
template), but the container was Up and serving within seconds.

**Destroy caveat (stacker bug, logged in root BUGS.md):**
`stacker destroy -y` printed ✓ but no-oped — `resolve_local_compose_project_name`
fails on `${BASE_PATH}` (not in AstrBot/.env) and falls back to `-p stacker`.
Cleanup done manually: `docker compose -p astrbot -f .stacker/docker-compose.yml down`.
