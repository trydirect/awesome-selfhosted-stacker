# [BUG] libredesk: stacker leaves service env uninterpolated + strong password policy

## Status: BLOCKED

## Summary
Two issues:
1. libredesk needs many LIBREDESK_DB__* / LIBREDESK_APP__* env vars. Missing
   any causes a koanf panic (\`db.max_open=0\`, \`app.log_level=\`, etc.).
2. Even with all vars set, the generated compose leaves some service-level env
   values as literal \`\${DB_PASSWORD}\` (uninterpolated), so the app cannot
   authenticate to the db service. This is the same interpolation gap seen in
   invoiceninja.

## Root cause
- libredesk has a strict config schema (many required keys).
- Stacker does not interpolate top-level .env values into every service-level
  env var (observed for MARIADB_ROOT_PASSWORD / POSTGRES_PASSWORD).

## Expected
App connects to db and serves HTTP 9000.

## Actual
\`panic: invalid value: db.max_open=0\` (and similar) during restart loop.

## Workaround
Provide a complete libredesk config.toml via bind-mount and set the password
policy-compliant admin password (uppercase+lowercase+number+special).

## Reproduction
```bash
cd stacker-projects/libredesk
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-10
