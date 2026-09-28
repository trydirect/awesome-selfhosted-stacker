# n8n — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): generator syncs contract-named keys
(`DB_POSTGRESDB_PASSWORD`/`POSTGRES_PASSWORD` → `DB_PASSWORD`;
`N8N_BASIC_AUTH_PASSWORD` → `ADMIN_PASSWORD`; `N8N_BASIC_AUTH_USER=admin`;
`N8N_BASIC_AUTH_ACTIVE=true` — the latter two are booleans/usernames wrongly
declared `generated: alphanumeric` in the contract). `ADMIN_PASSWORD` itself hit the
documented sed silent no-op (missing line) — appended.

## Verification

| Check | Result |
|---|---|
| Containers | `n8n-app-1` Up, `n8n-postgres-1` (healthy) |
| HTTP `GET /` (5678) | **200** |
