# Invoice Ninja — Local Deploy Success

## Result: SUCCESS

- **Image:** `invoiceninja/invoiceninja:latest`
- **Host port:** 8080
- **Deployments:** #1339
- **Verified:** DEPLOYED (db+app Up, migrations run) — no web server in image

## Commands used
```bash
cd stacker-projects/invoiceninja
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test
```

## Verification
- Deploy OK. db(mariadb) \`healthy\`, app php-fpm + queue workers running.
- Migrations completed (\`Running migrations ... DONE\`).
- **Blocker:** image has no nginx — nothing on :80, HTTP hangs. See BUGS.md.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-10
