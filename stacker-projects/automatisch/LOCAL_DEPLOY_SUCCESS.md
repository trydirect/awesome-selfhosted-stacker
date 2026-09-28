# automatisch — Local Deploy Success

**Date:** 2026-09-25
**Target:** local (`--target local` override; file default is `deploy.target: server`)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fixes applied (with user confirmation)

1. Secret name aligned with the contract field: `DB_PASSWORD` → `POSTGRES_PASSWORD`
   in `stacker.yml` placeholders, `.env`, `.env.example`, `scripts/generate-secrets.sh`
   (the renderer rewrites the placeholder to the env-key/contract name — see `BUGS.md`).
2. `app.platform: linux/amd64` attempted and **removed again** — silently dropped by
   the parser/generator (see `BUGS.md`); workaround used instead.

## Commands

```bash
cd stacker-projects/automatisch
set -a; source ../../.env; set +a
stacker config validate                       # ✓ valid
docker network create default_network         # missing external network (see BUGS.md)
docker pull --platform linux/amd64 postgres:16-alpine redis:7-alpine caddy:2-alpine
DOCKER_DEFAULT_PLATFORM=linux/amd64 stacker deploy --target local
```

The `DOCKER_DEFAULT_PLATFORM` export is required on this arm64 Mac because
`trydirect/automatisch:latest` is amd64-only; sidecar images were pulled for the same
platform so the stack is arch-consistent. The pre_build hook
(`scripts/generate-secrets.sh`) ran fine during deploy.

## Verification

| Check | Result |
|---|---|
| `stacker config validate` | ✓ valid |
| Containers | `app`, `automatisch-db` (healthy), `redis` (healthy), `caddy` — all Up |
| HTTP `GET http://localhost:3000/` | **200** |
| HTTP `GET http://localhost:80/` (caddy) | **200** |
| App logs | `Server is listening on http://localhost:3000`, no DB auth errors |
| DB check | `psql -U automatisch -d automatisch -c "select 1"` → ok (proves `POSTGRES_PASSWORD` reaches both app and db) |
| Compose warnings | none (previously `POSTGRES_PASSWORD variable is not set` ×2) |

## Notes

- 3 deploy failures were hit and logged in `BUGS.md` before this success:
  placeholder rewrite (blank DB password), amd64-only image, missing external
  `default_network` for `monitoring.status_panel: true`.
- `config_contract` on `automatisch-db` still carries junk editable fields
  (`healthcheck`, `interval`, `retries`, `test`, `timeout`, `volumes`) — cosmetic,
  not deploy-blocking (logged).
