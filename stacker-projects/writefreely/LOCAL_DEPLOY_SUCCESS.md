# writefreely — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (stacker bug workaround): renamed `Dockerfile` → `Dockerfile.custom`
(+ `app.dockerfile` updated) — the compose path normalizer rewrites
`dockerfile: Dockerfile` to `.stacker/Dockerfile`, which is never generated when
`app.dockerfile` is set explicitly. Root `BUGS.md` has the bug report.

## Verification

| Check | Result |
|---|---|
| Containers | `writefreely-app-1` + `writefreely-mysql-1` (healthy, in network) |
| HTTP `GET /` (8082) | **200** (WriteFreely HTML) |
