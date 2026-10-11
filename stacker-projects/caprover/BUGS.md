# [FIXED] caprover port 80 conflict with Stacker's caddy proxy

## Status: FIXED / VERIFIED

## Summary
CapRover's installer self-checks on port 80, but Stacker's always-on caddy
reverse proxy already binds 80/443 on every stacker server. The deploy failed
with a W001 port_conflict.

## Resolution (2026-10-11)
- Removed host-port `80:80` from `stacker.yml` (no longer exposed).
- Added `BY_PASS_PROXY_CHECK=TRUE` — the installer skips its :80 self-check.
- Added `MAIN_NODE_IP_ADDRESS=127.0.0.1` — the installer stops probing a
  public IP that caddy already owns.

Result: HTTP 200 on :3000. See `LOCAL_DEPLOY_SUCCESS.md`.

## Environment
- Test server: 46.224.127.228
- Deployments: #1342, #1343
