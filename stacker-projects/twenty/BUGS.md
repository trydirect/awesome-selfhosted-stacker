# [BUG] twenty entrypoint hardcodes psql to local socket

## Status: BLOCKED

## Summary
twenty's docker-entrypoint runs \`psql\` against a local unix socket
(\`/run/postgresql/.s.PGSQL.5432\`), ignoring DATABASE_URL / DB_HOST env vars.
It cannot reach the stacker \`db\` service.

## Root cause
The image's entrypoint calls psql without a host, defaulting to the local
socket. Setting DATABASE_URL does not change the migration step's psql target.

## Expected
Migrations run against the stacker \`db\` postgres service.

## Actual
\`psql: error: connection to server on socket ... failed\` in a restart loop.

## Workaround
Fork the image to honor DB_HOST in the migration psql call, or run migrations
manually. Not fixable from stacker.yml alone.

## Reproduction
```bash
cd stacker-projects/twenty
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-10
