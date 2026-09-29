# pingvin-share — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed.

## Verification

| Check | Result |
|---|---|
| Container | `pingvin-share-app-1` Up (healthy) |
| HTTP `GET /` (3000) | **200** |

## Server test: BLOCKED (platform auth expired)

`stacker deploy --target server` fails with `Authentication token expired. Run:
stacker login` (session expired 2026-09-28T17:30Z). Login is interactive (browser
OAuth or `stacker login -u <email>` + password) — cannot be completed autonomously.
Resume after `stacker login`.
