# komga — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed (junk `volumes: editable` contract field — known class).

## Verification

| Check | Result |
|---|---|
| Container | `komga-app-1` Up |
| HTTP `GET /` (25600) | **200** |
