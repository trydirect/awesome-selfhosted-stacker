# rallly — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. `DATABASE_URL` composed value written to `.env` (contract declares it generated —
   renderer keeps `${DATABASE_URL}`; calcom class).
2. `POSTGRES_PASSWORD` synced to `DB_PASSWORD` (contract `rallly-db` field; hanko class).
3. **Env schema drift:** current `lukevella/rallly` requires `SECRET_PASSWORD`
   (renamed from `SECRET`) and `SUPPORT_EMAIL` — template updated (env + contract +
   generator). Zod boot check failed with `Invalid environment variables` before.

## Verification

| Check | Result |
|---|---|
| Containers | `rallly-app-1` (healthy), `rallly-rallly-db-1` (healthy), caddy |
| HTTP `GET /` (3000) | **200** |
