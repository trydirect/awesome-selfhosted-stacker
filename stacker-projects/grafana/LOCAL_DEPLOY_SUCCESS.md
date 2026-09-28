# grafana — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fix (pre-approved class): contract field `GF_SECURITY_ADMIN_PASSWORD`
required an equally-named `.env` key (renderer keeps `${KEY}` for contract fields),
but the generator only wrote `ADMIN_PASSWORD`. Generator + `.env.example` now
produce `GF_SECURITY_ADMIN_PASSWORD` too.

## Verification

| Check | Result |
|---|---|
| Container | `grafana-app-1` Up, `0.0.0.0:3000->3000/tcp` |
| HTTP `GET /` | 302 → `/login`, `<title>Grafana</title>` |
