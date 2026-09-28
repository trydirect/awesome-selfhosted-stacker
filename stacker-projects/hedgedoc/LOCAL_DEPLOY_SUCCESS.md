# hedgedoc — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed. Contract fields (`DB_PASSWORD`, `SESSION_SECRET`) are
embedded in value templates of non-contract keys → resolve from `.env` at render
as designed; generator covers both names.

## Verification

| Check | Result |
|---|---|
| Containers | `hedgedoc-app-1` (healthy), `hedgedoc-postgres-1` (healthy) |
| HTTP `GET /` | **200**, `<title>HedgeDoc - Ideas grow better together</title>` |

Pre-steps: `docker stop stacker-bdd-pg stacker-bdd-pg-2` (5432 collision), grafana
local torn down (3000). Both restored after.
