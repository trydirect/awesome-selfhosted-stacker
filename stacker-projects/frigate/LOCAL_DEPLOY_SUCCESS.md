# frigate — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fixes applied (pre-approved class — see root `BUGS.md`)

1. **Host port remapped** `"5000:5000"` → `"5001:5000"` — macOS AirPlay Receiver
   (`ControlCenter`) owns 5000 locally and the platform Status Panel owns 5000 on
   managed boxes (logged as [NOTE] in root `BUGS.md`).
2. **Added a `deploy:` block** (`target: server` + `server.host/user/ssh_key`) — the
   template had none, so `--target server` failed with E002 ("Server host is required").

## Known open issue

`app.privileged: true` is **silently dropped** by the compose generator
(`docker inspect` → `privileged=false`) — logged in root `BUGS.md`. Frigate runs
without device access as a result; the web UI works, hardware capture would not.

## Commands

```bash
cd stacker-projects/frigate
./scripts/generate-secrets.sh
set -a; source ../../.env; set +a
stacker config validate       # ✓ valid
stacker deploy --target local
```

## Verification

| Check | Result |
|---|---|
| Container | `frigate-app-1` Up (healthy), `0.0.0.0:5001->5000/tcp` + 8554/8555 |
| HTTP `GET /` (5001) | **200** |
| Contract field `FRIGATE_RTSP_PASSWORD` | generated; name matches `.env` ✓ |
| `privileged` in render | **absent** (bug — see above) |

## Notes

- `ghcr.io/blakeblackshear/frigate:stable` is multi-arch — no platform workaround.
- `/dev/bus/usb:/dev/bus/usb` bind renders; on macOS Docker Desktop it materialises
  as an empty dir (documented bind-mount class) — harmless for the web UI test.
- Junk `volumes: {mutability: editable}` contract field (known cosmetic class).
