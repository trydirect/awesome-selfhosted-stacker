# FreeScout — Local Deploy Success

## Result: SUCCESS

- **Image:** `bfren/freescout:latest`
- **Host port:** 8082
- **Deployments:** #1353, #1354, #1355, #1356
- **Verified:** HTTP 200 on `/login`

## Fix applied

Three issues resolved:

1. **No postgres driver.** The bfren/freescout image ships only `pdo_mysql`,
   not `pdo_pgsql`, so a postgres db gave `could not find driver`. Switched the
   db service to `mysql:8.0` (`FREESCOUT_DB_CONN=mysql`, port 3306,
   `MYSQL_*` env) and added `ROOT_PASSWORD` for the healthcheck.

2. **Stale `/data` volume.** On a dirty `/data` volume the init failed at
   `mv: can't remove '/data/Modules': Is a directory` (leftover from prior
   partial runs). A clean volume lets init complete.

3. **Healthcheck false-negative.** `curl -fs http://localhost:80` fails on the
   302 → `/login` redirect. Changed to `curl -fsL` so it follows the redirect.

Note: the AIO/all-in-one split-stack variants are unnecessary here; the image
embeds nginx+php and only needs mysql.

## Commands used
```bash
cd stacker-projects/freescout
./scripts/generate-secrets.sh
# wipe stale data volume before deploy (init requires clean /data)
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test --force-rebuild
```

## Verification
- `curl -o /dev/null -w "%{http_code}" http://46.224.127.228:8082/` → `302`.
- `curl -L` follows to `/login` → `200`.
- MySQL `db` service healthy; app container up.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-11
