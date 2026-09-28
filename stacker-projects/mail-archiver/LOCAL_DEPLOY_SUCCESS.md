# mail-archiver — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (default)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. Empty `config_contract` block → volume policies (`mailarchiver_keys`,
   `mailarchiver_postgres_data`: generated).
2. Port 5000 → 5002 (AirPlay/statuspanel class; `public_ports` synced).
3. `deploy.server` block added (was absent — E002 for `--target server`).

## Verification

| Check | Result |
|---|---|
| Containers | `mail-archiver-app-1` Up, `mail-archiver-postgres-1` (healthy) |
| HTTP `GET /` (5002) | 302 → `/Auth/Login` → **200** |
