# kopia — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture fixes needed (`KOPIA_PASSWORD` generator is name-aligned; `app.command`
present).

## Verification

| Check | Result |
|---|---|
| Containers | `kopia-app-1` Up, caddy |
| HTTP `GET /` (51515) | **401** — auth enforced (expected unauthenticated) |
