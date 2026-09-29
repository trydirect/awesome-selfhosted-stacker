# screego — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. **Image tag**: `ghcr.io/screego/server:latest` does not exist — registry has
   version tags only (`1`, `1.11.x`, arch-suffixed). Switched to `:1` (multi-arch).
2. **Env schema drift**: `SCREEGO_EXTERNAL_IP: auto` → `127.0.0.1` placeholder.
   Current version rejects `auto` and `ipify` (`invalid SCREEGO_EXTERNAL_IP`) and
   rejects empty (`SCREEGO_EXTERNAL_IP or SCREEGO_TURN_EXTERNAL_IP must be set`).
   The field is contract-`editable` — buyers set their real IP.

## Verification

| Check | Result |
|---|---|
| Containers | `screego-app-1` Up, caddy |
| HTTP `GET /` (5050) | **200** |
