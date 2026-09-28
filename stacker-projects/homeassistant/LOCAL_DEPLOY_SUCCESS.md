# homeassistant — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed (junk `volumes: editable` contract field noted before —
known cosmetic class).

## Verification

| Check | Result |
|---|---|
| Containers | `homeassistant-app-1` Up (8123), `homeassistant-caddy-1` (proxy) |
| HTTP `GET /` | 302 → onboarding, `<title>Home Assistant</title>` |
