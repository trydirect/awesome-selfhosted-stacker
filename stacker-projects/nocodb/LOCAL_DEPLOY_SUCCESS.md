# nocodb — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (pre-approved class): contract-key syncs `NC_DB` (composed DSN) and
`POSTGRES_PASSWORD` in `.env` (generator writes `DB_PASSWORD` only).

## Verification

| Check | Result |
|---|---|
| Containers | `nocodb-app-1` + `nocodb-nocodb-db-1` (healthy) |
| HTTP `GET /` (8080) | **200** |
