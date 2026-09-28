# organizr — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes (standard junk `volumes: editable` contract field).

## Verification

| Check | Result |
|---|---|
| Container | `organizr-app-1` Up (healthy) |
| HTTP `GET /` (9983) | **200** |
