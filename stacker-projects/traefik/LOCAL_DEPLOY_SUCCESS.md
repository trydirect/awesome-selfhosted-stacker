# traefik — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (default after fix)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. Empty `config_contract` block → volume policy (`traefik_certs`).
2. `deploy.server` block added.
3. **`app.command` list form rejected** (`invalid type: sequence, expected a string`)
   — stringified the flag list; traefik accepts it (dashboard serves).

## Verification

| Check | Result |
|---|---|
| Container | `traefik-app-1` Up (80/443/8080) |
| HTTP `GET /dashboard/` (:8080) | **200** |

Notes: traefik logs a retrying docker-provider error on Docker Desktop
("Failed to retrieve information of the docker client") — non-fatal, dashboard works.

## Server test: BLOCKED (structural)
Host 80/443 collide with the platform-managed `caddy` on managed boxes (root
`BUGS.md`, same class as discourse/jitsi) — not attempted.
