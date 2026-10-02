# bookstack — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): contract-key syncs `DB_PASS`/`MYSQL_PASSWORD`/
`MYSQL_ROOT_PASSWORD`; added `APP_KEY` (image halts without it) + `APP_URL`
localhost; bind-mounted generated `bookstack.env` → `/config/www/.env` —
**the `lscr.io/linuxserver/bookstack` image ignores `DB_*` container env vars**
(config only via `/config/www/.env`), so the template's env-only DB wiring could
never work (Access denied for `database_username`). Added `deploy.server` (E002).

## Verification

| Check | Result |
|---|---|
| Containers | app + bookstack-db + traefik up |
| HTTP `GET /login` (6875) | **200** |
