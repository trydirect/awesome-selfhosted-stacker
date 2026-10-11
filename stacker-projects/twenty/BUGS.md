# [FIXED] twenty entrypoint hardcodes psql to local socket

## Status: FIXED / VERIFIED

## Summary
twenty's migration step ran `psql` against the local unix socket, ignoring
`DATABASE_URL` / `DB_HOST`, so it could not reach the stacker `db` service.

## Resolution (2026-10-11)
- Set `PG_DATABASE_URL` (the var the image's migration step actually honors)
  pointing at the `db` service.
- Set `SERVER_URL`, `REDIS_URL`, `ENCRYPTION_KEY`.
- Added a required `redis` service.

Result: HTTP 200 on :3000, migrations ran against `db`. See
`LOCAL_DEPLOY_SUCCESS.md`.

## Environment
- Test server: 46.224.127.228
- Deployment: #1347
