# calcom — Local Deploy Success

**Date:** 2026-09-26
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fix applied (with user confirmation)

`scripts/generate-secrets.sh` now generates `DATABASE_URL=postgresql://calcom:<DB_PASSWORD>@calcom-db:5432/calcom`
into `.env` (append-if-missing pattern); `.env.example` gained `DATABASE_URL=`.
Required because the renderer replaces contract-declared values with bare
`${KEY}` placeholders — see `BUGS.md` (renderer bug + fixture bug, both logged).

## Commands

```bash
cd stacker-projects/calcom
set -a; source ../../.env; set +a
stacker config validate                              # ✓ valid
./scripts/generate-secrets.sh                        # generates DATABASE_URL
DOCKER_DEFAULT_PLATFORM=linux/amd64 stacker deploy --target local   # amd64-only image
# one-time DB init (image does not run migrations on boot):
docker exec calcom-app-1 sh -c 'export DATABASE_DIRECT_URL="$DATABASE_URL"; npx prisma migrate deploy'
```

Note: `stacker deploy` initially refused a port-3000 conflict (previous test's
stack) — the preflight worked as designed; freed the port and retried.

## One-time initialization (documented per SKILL.md §4)

- `npx prisma migrate deploy` inside the app container applies the full schema
  (`All migrations have been successfully applied`, incl. `users`).
- The migrate CLI requires `DATABASE_DIRECT_URL` (Prisma `directUrl`); the running
  app does not. Set it inline for the migrate step.

## Verification

| Check | Result |
|---|---|
| `stacker config validate` | ✓ valid |
| Containers | `calcom-app-1` Up, `calcom-calcom-db-1` (healthy) |
| Container `DATABASE_URL` | set (was empty pre-fix) |
| HTTP `GET /` | 307 → `GET /auth/setup?step=1` → **200** (first-run wizard) |
| HTTP `GET /api/me` | 409 (expected before setup) |
| Schema | `users` + full cal.com schema present in `calcom` DB |
| Logs after init | no errors; earlier `P2021 table does not exist` stopped after migration |

## Notes

- `calcom/cal.com:latest` is amd64-only — `DOCKER_DEFAULT_PLATFORM=linux/amd64`
  required locally (same as automatisch).
- Residual log noise (non-fatal): `getDeploymentKey: Signature token not found…`
  and a `react-i18next` warning — cosmetic.
- Recommended fixture follow-ups (logged in `BUGS.md`): bake
  `app.command: sh -c "npx prisma migrate deploy && yarn start"` so first boot
  self-initialises, and add `DATABASE_DIRECT_URL` to the generator.
