# network-tools — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes: empty `config_contract` block removed; `deploy.server` block added.
Utility container (`ENTRYPOINT ["sleep","infinity"]`) — no HTTP surface; verification
is container state + tool exec.

## Verification

| Check | Result |
|---|---|
| Container | `network-tools-app-1` Up |
| `docker exec … curl --version` | ✓ curl 8.14.1 (x86_64-alpine) |

Notes: `app.image` takes precedence over `app.dockerfile` (mutually exclusive) — the
checked-in Dockerfile is dead code; the amd64-only `trydirect/network-tools:latest`
needs `DOCKER_DEFAULT_PLATFORM=linux/amd64` locally.
