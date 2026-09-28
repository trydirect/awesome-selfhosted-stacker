# chatwoot — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fixes applied (with user confirmation — see `BUGS.md`)

1. `generate-secrets.sh`: also generates `POSTGRES_PASSWORD` + composed `DATABASE_URL`
   (contract-name alignment; append-if-missing pattern). `.env.example` extended.
2. `app.command: sh docker/entrypoints/rails.sh sh -c "bundle exec rails db:prepare && mkdir -p tmp/pids && bundle exec puma -C config/puma.rb"` —
   the `develop-ce` image defaults to `cmd=[irb]`; its rails.sh ends with `exec "$@"`
   (needs the server as args) and runs no migrations.
3. `chatwoot-db` image: `postgres:16-alpine` → `pgvector/pgvector:pg16` (migrations
   require the `vector` extension).

## Commands

```bash
cd stacker-projects/chatwoot
set -a; source ../../.env; set +a
./scripts/generate-secrets.sh
stacker config validate                       # ✓ valid
stacker deploy --target local --force-rebuild
```

## Verification

| Check | Result |
|---|---|
| Containers | `chatwoot-app-1` Up (stable), `chatwoot-db` (healthy), `chatwoot-redis` (healthy), `caddy` |
| HTTP `GET /` | 302 → `/installation/onboarding` → **200** (first-run wizard) |
| `db:prepare` | succeeded (pgvector available; schema created) |
| Puma | listening on 0.0.0.0:3000, no restart loop |
| Compose warnings | none |

## Notes

- Troubleshooting path: `cmd=[irb]` crash-loop → missing `exec "$@"` args →
  pgvector extension → missing `tmp/pids`. Each logged in `BUGS.md`.
- Calcom's local stack was torn down first (port-3000 conflict; stacker's preflight
  reports these clearly).
- caddy included locally (proxy.type: caddy) but excluded on remote deploys as
  platform-managed.
