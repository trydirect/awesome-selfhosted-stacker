# syncthing — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (default after fix)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix: `deploy.server` block added (E002 class).

## Verification

| Check | Result |
|---|---|
| Container | `syncthing-app-1` Up (8384 + 22000 tcp/udp) |
| HTTP `GET /` (8384) | **200** |
