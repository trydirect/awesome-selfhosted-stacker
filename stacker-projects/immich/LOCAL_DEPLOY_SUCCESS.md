# immich — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. `POSTGRES_PASSWORD` synced to `DB_PASSWORD` (split contract fields share one
   value — the hanko pattern).
2. `deploy.server` block added (`server: null` → standard env-based block).

## Verification

| Check | Result |
|---|---|
| Containers | `immich-app-1` (healthy), `immich-immich-db-1` (healthy), `immich-immich-redis-1` (healthy) |
| HTTP `GET /` (2283) | **200** |
