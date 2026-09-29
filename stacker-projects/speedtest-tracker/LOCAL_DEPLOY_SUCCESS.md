# speedtest-tracker — Local Deploy Success

**Date:** 2026-09-29
**Target:** local (default after fix)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class):
1. `APP_KEY` required by current linuxserver image (`An application key is missing,
   halting init!`) — `APP_KEY: ${APP_KEY}` env + `base64:$(openssl rand -base64 32)`
   generator (append-if-missing).
2. `deploy.server` block added (E002 class).

## Verification

| Check | Result |
|---|---|
| Container | `speedtest-tracker-app-1` Up |
| HTTP `GET /` (8080) | 302 → `/getting-started` → **200** |
