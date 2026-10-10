# FossBilling — Local Deploy Success

## Result: SUCCESS

- **Image:** `fossbilling/fossbilling:latest`
- **Host port:** 8083
- **Deployments:** #1305
- **Verified:** HTTP 307 (install wizard redirect)

## Commands used
```bash
cd stacker-projects/fossbilling
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test
```

## Verification
- \`curl localhost:8083\` → \`307\` (redirect to install wizard — normal first-run).
- App + db(mariadb) both \`Up healthy\`.
- Port 8083 (80 taken by Stacker caddy).

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-10
