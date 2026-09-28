# keycloak — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (pre-approved class): generator syncs contract-named keys
(`KC_DB_PASSWORD`, `POSTGRES_PASSWORD` → `DB_PASSWORD`; `KEYCLOAK_ADMIN_PASSWORD` →
`ADMIN_PASSWORD`; `KEYCLOAK_ADMIN=admin`) — the split-shared-value + name-alignment
classes.

## Verification

| Check | Result |
|---|---|
| Containers | `keycloak-app-1` Up, `keycloak-keycloak-db-1` (healthy), caddy |
| HTTP `GET /` (8080) | 302 → `/admin/master/console/` → **200** |
