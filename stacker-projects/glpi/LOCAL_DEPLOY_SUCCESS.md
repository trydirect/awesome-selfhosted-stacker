# GLPI — Local Deploy Success

## Result: SUCCESS

- **Image:** `glpi/glpi:latest`
- **Host port:** 8081
- **Deployments:** #1330
- **Verified:** HTTP 200

## Commands used
```bash
cd stacker-projects/glpi
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test
```

## Verification
- \`curl localhost:8081\` → \`200\`.
- Container \`status=running restarts=0\`.
- ITSM helpdesk reachable.

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-10
