# Diun — Local Deploy Success

## Result: SUCCESS

- **Image:** `ghcr.io/crazy-max/diun:latest`
- **Host port:** —
- **Deployments:** #1296
- **Verified:** daemon running restarts=0

## Commands used
```bash
cd stacker-projects/diun
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test
```

## Verification
- Fixed env: \`DIUN_PROVIDERS_DOCKER=true\`, \`DIUN_PROVIDERS_DOCKER_WATCHBYDEFAULT=true\`, \`DIUN_WATCH_SCHEDULE=@every 5m\`.
- Container \`status=running restarts=0\` after cron cycle.
- Logs: \`Found 4 image(s) to analyze\`, \`Jobs completed\`.
- Headless update-notifier daemon (no HTTP UI).

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-10
