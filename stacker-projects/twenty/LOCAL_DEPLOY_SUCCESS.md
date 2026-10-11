# Twenty — Local Deploy Success

## Result: SUCCESS

- **Image:** `twentycrm/twenty:latest`
- **Host port:** 3000
- **Deployments:** #1347
- **Verified:** HTTP 200

## Fix applied

The migration step needs `PG_DATABASE_URL` (not `DATABASE_URL` / `DB_HOST`) so
`psql` targets the stacker `db` service instead of the local socket:
- Set `PG_DATABASE_URL=postgres://...@db:5432/...`.
- Set `SERVER_URL`, `REDIS_URL`, `ENCRYPTION_KEY`.
- Added a `redis` service (required by twenty).

## Commands used
```bash
cd stacker-projects/twenty
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test --force-rebuild
```

## Verification
- `curl -o /dev/null -w "%{http_code}" http://46.224.127.228:3000/` → `200`.
- All containers healthy; Nest server started; migrations ran against `db`.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-11
