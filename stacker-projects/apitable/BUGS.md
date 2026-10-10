# [BUG] apitable all-in-one ignores external DB (connects as root@localhost)

## Status: BLOCKED

## Summary
apitable/all-in-one bundles its own MySQL/rabbitmq/minio and ignores the
external \`db\` service. Its databus-server connects as \`root\` to a local
MySQL that isn't the stacker \`db\` service, panicking with auth errors.

## Root cause
The all-in-one image expects to own the entire data stack. Stackers external-db
pattern (app + db service) is incompatible.

## Expected
App connects to the stacker \`db\` postgres/mysql service.

## Actual
\`databus-server\` panics: \`Access denied for user 'root'@'...'\`.

## Workaround
Use a compose-based APITable deployment (not the all-in-one) with explicit
backend/frontend/databus services. Not supported by the single-app stacker model.

## Reproduction
```bash
cd stacker-projects/apitable
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-10
