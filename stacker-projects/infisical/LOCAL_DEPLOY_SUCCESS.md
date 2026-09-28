# infisical — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. **Added `infisical-redis` service + `REDIS_URL`** — the app hard-requires Redis
   (`Either REDIS_URL, REDIS_SENTINEL_HOSTS or REDIS_CLUSTER_HOSTS must be defined`)
   and the template shipped none.
2. **`DB_CONNECTION_URI` + `POSTGRES_PASSWORD`** generator entries (contract-key
   name alignment: composed URL field + split shared password — calcom/hanko classes).

## Verification

| Check | Result |
|---|---|
| Containers | `infisical-app-1` Up, `infisical-db` (healthy), `infisical-redis` (healthy) |
| HTTP `GET /` (8080) | **200** |
