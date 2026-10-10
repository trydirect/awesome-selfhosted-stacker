# LibreNMS — Local Deploy Success

## Result: SUCCESS

- **Image:** `librenms/librenms:latest`
- **Host port:** 8000
- **Deployments:** #1321
- **Verified:** HTTP 302 (install redirect)

## Commands used
```bash
cd stacker-projects/librenms
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test
```

## Verification
- \`curl localhost:8000\` → \`302\` (redirect to install wizard — normal first-run).
- App + mariadb + redis all \`Up healthy\`.
- Logs: \`artisan schedule:run\` cron running.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-10
