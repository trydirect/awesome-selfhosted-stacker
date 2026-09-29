# paperless-ngx — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. Generator syncs contract-named keys: `PAPERLESS_DBPASS`/`POSTGRES_PASSWORD` →
   `DB_PASSWORD`, `PAPERLESS_ADMIN_PASSWORD` → `ADMIN_PASSWORD`,
   `PAPERLESS_SECRET_KEY` → `SECRET_KEY` (grafana/hanko classes).
2. Redis host port `127.0.0.1:6379` → `127.0.0.1:6380` — the platform User Service
   dev container (`user-redis-1`) owns 6379 (left untouched).

## Verification

| Check | Result |
|---|---|
| Containers | app (healthy), db (healthy), redis (healthy) |
| HTTP `GET /` (8000) | 302 → `/accounts/login/` → **200** |

Notes: first boot runs migrations/indexing (`health: starting` ~1 min). The skeleton
style of the YAML (`dockerfile: null` etc.) triggers "empty structural path" config
warnings — informational only.
