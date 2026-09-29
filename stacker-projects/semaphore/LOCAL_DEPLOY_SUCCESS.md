# semaphore — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes (contract fields are placeholder names — bake path). Pre-steps:
tore down rocket-chat (3000) + redash (5432) local stacks; bdd-pg paused.

## Verification

| Check | Result |
|---|---|
| Containers | `semaphore-app-1` Up, `semaphore-postgres-1` (healthy) |
| HTTP `GET /` (3000) | **200** |

Notes: half-broken stack residue (app started during a failed port-bind attempt)
needed the proven full `down -v` + fresh redeploy.
