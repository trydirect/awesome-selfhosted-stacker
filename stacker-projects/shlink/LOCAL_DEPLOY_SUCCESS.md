# shlink — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-19

## Commands used

```bash
cd stacker-projects/shlink
./scripts/generate-secrets.sh
stacker deploy --target local
```

Two blocking issues had to be resolved first — see `BUGS.md` and the
upstream issues filed:

1. `GEOLITE_LICENSE_KEY: "${GEOLITE_LICENSE_KEY:-}"` in `stacker.yml` used
   bash-style default-value substitution, which stacker's `${VAR}`
   resolver doesn't support at all (fails even when the var is set).
   Fixed by changing to plain `${GEOLITE_LICENSE_KEY}` and adding an empty
   `GEOLITE_LICENSE_KEY=` to `.env`/`.env.example`.
   Root cause: [stacker#235](https://github.com/trydirect/stacker/issues/235)
   is unrelated; this substitution gap wasn't filed separately since it's
   covered by the `${VAR_NAME}`-only doc note in `SKILL.md` §6 — see
   `BUGS.md` for detail.
2. `stacker deploy --target local` reuses a global, unnamespaced Compose
   project name (`stacker`) and volume name (`postgres_data` →
   `stacker_postgres_data`) shared by every project in this repo. The
   volume still held data from an earlier, differently-configured local
   deploy, so Postgres skipped its init scripts and shlink's app couldn't
   authenticate as the `shlink` role. Fixed by removing the stale
   `stacker_postgres_data` volume and letting it re-init cleanly. Filed
   upstream as [stacker#235](https://github.com/trydirect/stacker/issues/235)
   (high severity — this affects every project's local deploy in this repo).

## Verification

- `docker ps` → `stacker-app-1` (shlinkio/shlink:latest) and
  `stacker-postgres-1` (postgres:16-alpine) both up.
- `curl http://localhost:8080/rest/health` →
  `{"status":"pass","version":"5.1.5",...}`
- `docker exec stacker-app-1 shlink api-key:generate` → API key generated
  successfully (proves DB connectivity + migrations succeeded).
- Full round trip via REST API:
  - `POST /rest/v3/short-urls` with `X-Api-Key` → created short URL
    `H16X0` for `https://example.com`.
  - `curl -I http://localhost:8080/H16X0` → `302 Found`,
    `Location: https://example.com` — redirect works end-to-end.

No remaining stacker or shlink bugs blocking local deploy once the two
issues above were worked around.
