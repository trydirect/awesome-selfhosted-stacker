# hermes-agent — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fixes applied (pre-approved class)

1. **`command: sleep infinity`** — the image's documented headless invocation. Without
   it the CMD runs the interactive TUI, sees non-TTY stdin, prints "Goodbye! ☤" and
   tears the s6 stack (incl. the dashboard) down. The `main-hermes` s6 service is a
   no-op by design; CMD = the container's main program.
2. **Dashboard enabled**: `HERMES_DASHBOARD: '1'`, `HERMES_DASHBOARD_PORT: '8000'`
   (template maps 8000/8001), basic auth (`HERMES_DASHBOARD_BASIC_AUTH_USERNAME` +
   generated `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` — name-aligned contract field
   + generator entry). The dashboard's auth gate requires a provider on non-loopback
   binds (fail-closed since the June 2026 hardening).
3. **Hardcoded stale server normalized**: `deploy.server.host: 116.202.19.183` →
   `${EXISTING_SERVER_HOST}`, absolute ssh_key path → `${BASE_PATH}/…`.

## Verification

| Check | Result |
|---|---|
| Container | `hermes-agent-app-1` Up (stable) |
| HTTP `GET /` (8000) | 302 → `/login?next=%2F` → **200** (Hermes Web UI) |

## Notes

- Port 8001 is mapped but nothing binds it (gateway service is opt-in/profile-based).
- Preflight own-container exclusion gap recurred (druid case) — `down` before redeploy.
