# linkwarden — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed (contract fields are placeholder names — bake fine;
generator covers `NEXTAUTH_SECRET`/`DB_PASSWORD`).

## Verification

| Check | Result |
|---|---|
| Containers | `linkwarden-app-1` (healthy), `linkwarden-postgres-1` (healthy) |
| HTTP `GET /` (3000) | **200** |

Notes: a half-broken stack residue (db container without network after a failed
port-bind attempt) caused `P1001: Can't reach database server`; full
`docker compose down -v` + fresh deploy fixed it.
