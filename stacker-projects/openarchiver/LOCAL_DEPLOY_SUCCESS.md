# openarchiver — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): added missing env vars the image actually
requires but the template omits — `DATABASE_URL` (composed), `STORAGE_TYPE=local`,
`ENCRYPTION_KEY`, `STORAGE_ENCRYPTION_KEY` (64-hex), `MEILI_HOST`
(default `127.0.0.1:7700` unreachable), `REDIS_HOST/REDIS_PORT`
(default `127.0.0.1:6379`), `PORT_BACKEND=3001`, `JWT_SECRET`, `JWT_EXPIRES_IN`;
added `deploy.server` (E002).

## Verification

| Check | Result |
|---|---|
| Containers | app, postgres (healthy), valkey (healthy), meilisearch (healthy), tika |
| HTTP `GET /` (3000) | 307 → `/setup` **200** |
