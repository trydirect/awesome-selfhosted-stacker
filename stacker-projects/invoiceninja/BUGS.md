# [BUG] invoiceninja image is php-fpm-only (no nginx) + service-env interpolation gap

## Status: BLOCKED

## Summary
invoiceninja/invoiceninja:latest boots php-fpm + queue workers via supervisord,
but the image ships **no nginx/web server**. There is nothing listening on :80,
so HTTP on the mapped host port hangs (connection established, no response).

Secondary issue: the db service's MARIADB_ROOT_PASSWORD is left as a literal
\`\${DB_ROOT_PASSWORD}\` in the generated compose (stacker does not interpolate
top-level .env into every service env var), which initially blocked MariaDB init.

## Root cause
- The image's supervisord.conf has no \`program:nginx\` — it expects an external
  reverse proxy in front of php-fpm :9000.
- Stackers service-env interpolation gap (same as libredesk).

## Expected
HTTP 200 on the mapped host port after migrations.

## Actual
php-fpm :9000 is up, queue workers running, but no web server. curl hangs.

## Workaround
Add an nginx sidecar service that proxies to the app's php-fpm, or use the
invoiceninja web image variant that bundles nginx.

## Reproduction
```bash
cd stacker-projects/invoiceninja
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-10
