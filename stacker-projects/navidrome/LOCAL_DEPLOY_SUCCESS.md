# navidrome — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed.

## Verification

| Check | Result |
|---|---|
| Containers | `navidrome-app-1` Up, `navidrome-caddy-1` (proxy) |
| HTTP `GET /` (4533) | 302 → `/app/` → **200** |
