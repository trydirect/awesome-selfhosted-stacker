# maybe-finance — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes (generator covers `SECRET_KEY_BASE`/`DB_PASSWORD`; contract fields
name-aligned).

## Verification

| Check | Result |
|---|---|
| Containers | `maybe-finance-app-1` Up, `maybe-finance-postgres-1` (healthy) |
| HTTP `GET /sessions/new` | **200**, `<title>Maybe</title>` |

Notes: `/` redirects to `https://…` (Rails force_ssl) with no TLS terminator in
local mode — probe `/sessions/new` directly. The app itself is healthy.
