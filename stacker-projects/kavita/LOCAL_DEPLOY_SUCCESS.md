# kavita — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix: host port 5000 → 5001 (macOS AirPlay Receiver owns 5000; platform
statuspanel owns 5000 on managed boxes — the frigate class; root `BUGS.md`).

## Verification

| Check | Result |
|---|---|
| Container | `kavita-app-1` Up, `0.0.0.0:5001->5000/tcp` |
| HTTP `GET /` | **200**, `<title>Kavita</title>` |
