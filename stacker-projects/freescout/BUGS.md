# [FIXED] freescout (bfren/freescout) s6 stack exits after boot

## Status: FIXED / VERIFIED

## Summary
bfren/freescout:latest started its s6 overlay services then shut them down,
entering a restart loop. Root causes (three, layered):

1. **No postgres driver.** The image ships only `pdo_mysql`, not `pdo_pgsql`,
   so a postgres db gave `could not find driver` and the installer could not
   run migrations.
2. **Stale `/data` volume.** Init failed at
   `mv: can't remove '/data/Modules': Is a directory` when leftover dirs from
   a prior partial run were present.
3. **Healthcheck false-negative.** `curl -fs` fails on the 302 → `/login`
   redirect.

## Resolution (2026-10-11)
- Switched db service to `mysql:8.0` (`FREESCOUT_DB_CONN=mysql`, `MYSQL_*`
  env, `ROOT_PASSWORD` for healthcheck).
- Use a clean `/data` volume (wipe before deploy).
- Healthcheck changed to `curl -fsL` (follow redirect).

Result: HTTP 302 on `/`, follows to `/login` → `200`. See
`LOCAL_DEPLOY_SUCCESS.md`.

## Environment
- Test server: 46.224.127.228
- Deployments: #1353, #1354, #1355, #1356
