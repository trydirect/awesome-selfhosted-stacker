# typebot — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): `DATABASE_URL` composed value in `.env`
(contract generated — calcom class); `POSTGRES_PASSWORD` + `NEXTAUTH_URL` synced
(`NEXTAUTH_URL` is declared `generated: alphanumeric` — URL nonsense — but the key
must resolve); `HOSTNAME: 0.0.0.0` added (see root `BUGS.md` dual-network note).

## Verification

| Check | Result |
|---|---|
| Containers | `typebot-app-1`, `typebot-typebot-db-1` (healthy), caddy |
| HTTP `GET /signin` (3001) | **200** |
