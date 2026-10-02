# wordpress-matomo — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): contract placeholder `WORDPRESS_DB_PASSWORD`
synced in `.env` (generator writes `DB_PASSWORD` only — name-mismatch class);
`matomo-db` healthcheck `mysqladmin` → `mariadb-admin` (not in `mariadb:11`).

## Verification

| Check | Result |
|---|---|
| Containers | app, matomo, matomo-db (healthy), wp-db (healthy) |
| HTTP `GET /` (8080 wordpress) | **200** |
| HTTP `GET /` (8081 matomo) | **200** |
