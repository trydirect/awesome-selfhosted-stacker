# docmost — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

**No fixture fixes needed** — first fully clean template of the campaign.

## Commands

```bash
cd stacker-projects/docmost
docker stop stacker-bdd-pg stacker-bdd-pg-2   # both bind 127.0.0.1:5432; restored after
./scripts/generate-secrets.sh
set -a; source ../../.env; set +a
stacker config validate        # ✓ valid
stacker deploy --target local
```

## Verification

| Check | Result |
|---|---|
| Containers | `docmost-app-1` Up (3000), `docmost-postgres-1` (healthy), `docmost-redis-1` (healthy) |
| HTTP `GET /` | **200**, `<title>Docmost</title>` |
| Secrets | `APP_SECRET`/`DB_PASSWORD` generated; composed `DATABASE_URL` baked correctly (non-contract key) |

## Notes

- Contract declares `APP_SECRET` + `DB_PASSWORD` — names match `.env` keys, so the
  `${KEY}` placeholder rendering works as designed. `DATABASE_URL` is not a contract
  key → its composed value (with embedded `${DB_PASSWORD}`) resolved at render.
- Healthchecks with plain-string `test:` render correctly through the pipeline.
- Template-leak extras in `generate-secrets.sh` (JWT_SECRET etc.) — harmless.
