# Netdata — Local Deploy Success

## Result: SUCCESS

- **Image:** `netdata/netdata:latest`
- **Host port:** 19999
- **Deployments:** #1298
- **Verified:** HTTP 200

## Commands used
```bash
cd stacker-projects/netdata
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test
```

## Verification
- \`curl localhost:19999\` → \`200\`.
- Container \`status=running (healthy)\`.
- Full observability dashboard on :19999.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-10
