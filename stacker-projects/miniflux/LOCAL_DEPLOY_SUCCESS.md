# miniflux — Local Deploy Success

**Target:** local (Docker, via stacker CLI)
**Date:** 2026-08-19

## Commands used

```bash
cd stacker-projects/miniflux
./scripts/generate-secrets.sh
stacker deploy --target local
```

`stacker.yml` references `${ADMIN_PASSWORD}` (for `CREATE_ADMIN`), but
`.env.example`/`generate-secrets.sh` never defined or generated it —
first attempt failed immediately with `Error: Environment variable not
found: $ADMIN_PASSWORD`. Fixed (with user confirmation) by adding
`ADMIN_PASSWORD=` to `.env.example` and matching generation logic to
`generate-secrets.sh`, following the same pattern as `DB_PASSWORD`/
`SECRET_KEY`. See `BUGS.md`.

Also cleared a stale `stacker_postgres_data` volume/container left over
from the previous project tested locally (`shlink`/`privatebin`) —
expected per the already-filed
[stacker#235](https://github.com/trydirect/stacker/issues/235) collision
bug, not re-investigated.

## Verification

- `docker ps` → `stacker-app-1` (miniflux/miniflux:latest) and
  `stacker-postgres-1` (postgres:16-alpine) both up.
- `curl -I http://localhost:8080/` → `HTTP/1.1 200 OK`, session cookie set.
- `curl http://localhost:8080/v1/me -u admin:$ADMIN_PASSWORD` → returned
  full admin user JSON (`"username":"admin","is_admin":true`), proving DB
  migrations ran and the admin account was created correctly.
- `curl -X POST http://localhost:8080/v1/feeds -u admin:$ADMIN_PASSWORD
  -d '{"feed_url":"https://miniflux.app/feed?category_id=1"}'` →
  `{"feed_id":1}` — full feed-subscription round trip works.

No remaining bugs blocking local deploy once `ADMIN_PASSWORD` was added.
