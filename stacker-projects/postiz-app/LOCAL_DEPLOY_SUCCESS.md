# postiz-app — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes — generator covers all contract names (`JWT_SECRET`,
`DB_PASSWORD`, `TEMPORAL_DB_PASSWORD`); `./dynamicconfig/` bind staged into
`.stacker/` (root `BUGS.md` bind-resolution class).

## Verification

| Check | Result |
|---|---|
| Containers | app + postiz-postgres (healthy) + postiz-redis (healthy) + temporal + temporal-postgresql (healthy) + temporal-elasticsearch — 6/6 Up |
| HTTP `GET /` (4007) | 307 → `/auth` → **200** |
