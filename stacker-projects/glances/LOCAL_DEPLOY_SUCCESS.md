# glances — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed (no secrets — no generator even present).

## Verification

| Check | Result |
|---|---|
| Container | `glances-app-1` Up, `0.0.0.0:61208->61208/tcp` |
| HTTP `GET /` | **200**, `<title>Glances</title>` |

## Notes

- `privileged: true` silently dropped by the generator (known bug) — glances web UI
  works regardless (docker.sock is mounted read-only).
- Junk contract fields (`privileged`, `volumes` as editable env fields — known class).
