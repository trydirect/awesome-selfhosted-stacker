# Akaunting — Local Deploy Success

## Result: SUCCESS

- **Image:** `akaunting/akaunting:latest`
- **Host port:** 8080
- **Deployments:** #1331
- **Verified:** HTTP 302 (install redirect)

## Commands used
```bash
cd stacker-projects/akaunting
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test
```

## Verification
- \`curl localhost:8080\` → \`302\` (redirect to install wizard — normal first-run).
- Apache + PHP running, \`status=running restarts=0\`.
- Logs: \`Apache/2.4.66 ... configured -- resuming normal operations\`.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-10
