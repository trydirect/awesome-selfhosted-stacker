# tautulli — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes.

## Verification

| Check | Result |
|---|---|
| Container | `tautulli-app-1` Up (8181) |
| HTTP `GET /` | 302 → `/welcome` → **200** |
