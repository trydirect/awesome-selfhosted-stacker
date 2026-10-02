# zitadel — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Fixture fixes (pre-approved class): contract placeholder `POSTGRES_PASSWORD` synced
in `.env` (generator writes `POSTGRES_ADMIN_PASSWORD` only — name-mismatch class);
`ZITADEL_DOMAIN=localhost` for local.

Notes: `.env` changes are not picked up by deploy unless `--force-rebuild`
(compose not regenerated) — recorded in root `BUGS.md` session notes.

## Verification

| Check | Result |
|---|---|
| Containers | app (healthy), postgres (healthy), redis |
| HTTP `GET /` (8080) | 302 → `/ui/console/` **200** |
| `/debug/ready` | **200** |
