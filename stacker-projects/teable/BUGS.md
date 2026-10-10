# [BUG] teable backend listens on :3002, not :3000 (connection reset)

## Status: BLOCKED

## Summary
teable's all-in-one image starts its Nest backend and a Next.js frontend on
internal port 3002. The template maps host 3000 -> container 3000, but nothing
listens on 3000, so HTTP gets \`connection reset\`.

## Root cause
teable's default ports: backend :3001, Next.js :3002, sandbox :7070.
The image does not expose a unified entrypoint on :3000.

## Expected
HTTP 200 on host port.

## Actual
HTTP 000 / connection reset on :3000. Container \`status=running\` but no
listener on the mapped port.

## Workaround
Map host port to 3002 (Next.js) and route /api to backend :3001. Requires a
custom nginx sidecar — out of scope for a single-app template.

## Reproduction
```bash
cd stacker-projects/teable
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-10
