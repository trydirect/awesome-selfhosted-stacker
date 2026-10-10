# [BUG] caprover port 80 conflicts with Stacker's caddy proxy

## Status: BLOCKED

## Summary
CapRover's installer self-checks on port 80, but Stacker's always-on caddy
reverse proxy already binds 80/443 on every stacker server. The deploy fails
with a W001 port_conflict.

## Root cause
- Stacker runs a persistent \`caddy\` container on 80/443 (platform ingress).
- caprover hardcodes an installer check on :80.
- caprover requires ports 80 (installer), 3000 (dashboard), 8080.

## Expected
Deploy succeeds, dashboard reachable on 3000.

## Actual
Deployment ends \`paused [port_conflict]\`.

## Workaround
None available without disabling Stacker's caddy ingress (not supported).

## Reproduction
```bash
cd stacker-projects/caprover
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-10
