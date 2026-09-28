# ombi — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes (junk `volumes: editable` contract field — known class).

## Verification

| Check | Result |
|---|---|
| Container | `ombi-app-1` Up |
| HTTP `GET /` (3579) | **200** |
