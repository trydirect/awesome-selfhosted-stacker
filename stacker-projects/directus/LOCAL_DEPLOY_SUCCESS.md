# directus — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Clean pass — generator covered all four contract-generated keys
(`DB_PASSWORD`, `KEY`, `SECRET`, `ADMIN_PASSWORD`), `deploy.server` present.

## Verification

| Check | Result |
|---|---|
| Containers | `directus-app-1` + `directus-directus-db-1` (healthy) |
| HTTP `GET /` (8055) | 302 → `/admin` **200** |
