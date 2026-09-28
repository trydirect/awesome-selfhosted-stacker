# mattermost — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (pre-approved class): generator produces
`MM_SQLSETTINGS_DATASOURCE` (composed URL — contract declares it generated so the
renderer keeps `${MM_SQLSETTINGS_DATASOURCE}`; calcom class) and `POSTGRES_PASSWORD`
(synced to `DB_PASSWORD`; hanko class).

Local run needs `DOCKER_DEFAULT_PLATFORM=linux/amd64` (mattermost-enterprise image
is amd64-only).

## Verification

| Check | Result |
|---|---|
| Containers | `mattermost-app-1` (healthy), `mattermost-mattermost-db-1` (healthy) |
| HTTP `GET /` (8065) | **200** |
