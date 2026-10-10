# Actual Budget — Local Deploy Success

## Result: SUCCESS

- **Image:** `actualbudget/actual-server:latest`
- **Host port:** 3000
- **Deployments:** #1315
- **Verified:** HTTP 200

## Commands used
```bash
cd stacker-projects/actual
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test
```

## Verification
- \`curl localhost:3000\` → \`200\`.
- Fixed: image serves on internal :5006, not :3000. Mapping changed to \`3000:5006\`.
- Container \`status=running\`.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-10
