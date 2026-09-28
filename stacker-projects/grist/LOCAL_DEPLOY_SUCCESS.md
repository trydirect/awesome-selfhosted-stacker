# grist — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix: added `APP_HOME_URL` to `.env.example` (it was only in `.env` — fresh
clones would fail `${APP_HOME_URL}` resolution at parse).

## Verification

| Check | Result |
|---|---|
| Container | `grist-app-1` Up, `0.0.0.0:8484->8484/tcp` |
| HTTP `GET /` | 302 → `/boot` → **200** |

## Notes

- `APP_HOME_URL` is an editable contract field → baked literally at render; the
  value in `.env` governs. Grist validates the request Host against it.
