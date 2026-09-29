# redash — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): port 5000→5003 (AirPlay/statuspanel class),
redis 127.0.0.1:6379→6380 (User Service dev redis).

One-time DB init (SKILL.md §4 class):
`docker exec redash-app-1 python /app/manage.py database create_tables`
(the image has no `redash` binary in PATH; python2.7-era build).

## Verification

| Check | Result |
|---|---|
| Containers | app + db (healthy) + redis (healthy) |
| HTTP `GET /` (5003) | 302 → `/setup` → **200** (after create_tables) |
