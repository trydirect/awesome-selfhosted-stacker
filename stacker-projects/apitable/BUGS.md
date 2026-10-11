# [BUG] apitable all-in-one: broken liquibase migration in image (upstream)

## Status: BLOCKED (upstream image bug)

## Summary
`apitable/all-in-one:latest` bundles its own MySQL/Redis/RabbitMQ/MinIO and is
architecturally the right single-container fit for Stacker (no external db).
However the image's bundled Liquibase migration fails out of the box with a SQL
syntax error, so backend-server never starts.

## Root cause
The image ships a changeset (`db/changelog/0.3/20200407_changeset.xml`) whose
SQL has a JVM system-property flag (`-DDB_ENGINE=mysqlclient_release_version`)
leaked into the ALTER TABLE statement:

```
... near '-DDB_ENGINE=mysqlclient_release_version change `describe` ...'
```

backend-server (Liquibase) exits with SIGINT after `Migration failed`. This is
an internal image bug, not fixable from `stacker.yml`.

## Expected
Liquibase migrates the bundled MySQL and the web UI serves on :80.

## Actual
`liquibase.exception.DatabaseException: You have an error in your SQL syntax`
→ `PM2 App [backend-server] exited with code [1] via signal [SIGINT]`, container
unhealthy, HTTP 000 on :8084.

## Workaround
None from the template. Options: pin a pre-regression `all-in-one` tag, or use
the full multi-service compose deployment (backend/room/databus + external
MySQL) which is far heavier than a single-app template. Documented as blocked.

## Notes
- Architecture confirmed correct: all-in-one self-manages data in `/apitable`
  volume; external `db` service is ignored (previous external-db attempt failed
  with `Access denied for user 'root'`).

## Reproduction
```bash
cd stacker-projects/apitable
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-11
