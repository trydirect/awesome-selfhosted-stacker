# romm — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (pre-approved class): generator syncs `MARIADB_PASSWORD` = `DB_PASSWD`
(contract generated env-key, split-value class); empty `SCREENSCRAPER_*`/
`RETROACHIEVEMENTS_API_KEY`/`STEAMGRIDDB_API_KEY` lines ensured for parse.
Contract uses the mixed legacy-lists + `fields:` format (both parse fine).

## Verification

| Check | Result |
|---|---|
| Containers | `romm-app-1` Up, `romm-romm-db-1` (healthy, mariadb) |
| HTTP `GET /` (8080) | **200** |
