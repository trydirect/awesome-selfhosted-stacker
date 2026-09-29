# rybbit — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes — generator covers all contract keys (`BETTER_AUTH_SECRET`,
`CLICKHOUSE_PASSWORD`, `POSTGRES_PASSWORD`) + `REDIS_PASSWORD`; undeclared
`BASE_URL`/`DISABLE_SIGNUP`/`MAPBOX_TOKEN` present in `.env` (bake path).
File binds `./clickhouse/config.d/*.xml` staged into `.stacker/` (bind class).

## Verification

| Check | Result |
|---|---|
| Containers | app + backend + clickhouse (healthy) + postgres (healthy) + redis (healthy) |
| HTTP `GET /` (3002) | **200** |
