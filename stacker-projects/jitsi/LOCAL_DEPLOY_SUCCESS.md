# jitsi — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (see `BUGS.md`): prosody `JICOFO_AUTH_PASSWORD` wiring; port mapping
`80:8000`/`443:8443` for the `unstable` image's unprivileged nginx.

## Verification

| Check | Result |
|---|---|
| Containers | prosody, jicofo, jvb, web — all Up (prosody stable after fix) |
| HTTP `GET /` (:80) | **200** |
| HTTPS `GET /` (:443) | **200**, `<title>Jitsi Meet</title>` |

## Server test
Blocked structurally (host 80/443 vs platform caddy) — see `BUGS.md`.
