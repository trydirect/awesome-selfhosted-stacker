# hanko — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fixes applied (see `BUGS.md`)

1. `HANKO_DATABASE_PASSWORD`/`POSTGRES_PASSWORD` synced to `DB_PASSWORD` (one value).
2. Bind mount `./config.yaml` → `../config.yaml` (compose-relative resolution).
3. Generator: append-if-missing for the contract-name keys.

One-time init: `docker run --rm --network hanko_app-network -v $PWD/config.yaml:/etc/config.yaml:ro ghcr.io/teamhanko/hanko:latest migrate up --config /etc/config.yaml` (55 migrations).

## Verification

| Check | Result |
|---|---|
| Containers | `hanko-app-1` Up, `hanko-hanko-db-1` (healthy) |
| HTTP `GET /` (8002) | **200** |
