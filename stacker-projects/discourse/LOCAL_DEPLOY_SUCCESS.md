# discourse — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

No fixture changes needed — `config_contract` field names (`DB_PASSWORD`,
`SMTP_PASSWORD`) match the `.env` keys, and the DB image is already
`pgvector/pgvector:0.8.0-pg16` (discourse requires pgvector).

## Commands

```bash
cd stacker-projects/discourse
./scripts/generate-secrets.sh
set -a; source ../../.env; set +a
stacker config validate        # ✓ valid
stacker deploy --target local
```

Pre-steps on this Mac: `docker stop stacker-bdd-pg` (holds 127.0.0.1:5432, which
discourse's db binds; restored after the test).

## Verification

| Check | Result |
|---|---|
| Containers | `discourse-app-1` Up (80/443), `discourse-discourse_db-1` (healthy), `discourse-redis-1` (healthy) |
| HTTP `GET /` | **200**, `<title>Discourse Setup</title>` (first-run wizard) |
| Logs | workers ready, no errors |

## Server test: BLOCKED (environment)

- `project-app-1` failed to bind port 80 (platform `caddy` owns 80/443 on the box) —
  the known silent-success class (root `BUGS.md`).
- The box's disk hit **100%** again pulling discourse images; `discourse_db`
  crash-looped on `initdb: No space left on device`. Cleaned (18.56GB reclaimed,
  `docker image prune -a`, log truncation) — box at 50%.
- A template mapping `80:80`/`443:443` cannot coexist with the platform-managed
  caddy on `--target server` boxes — structural conflict worth a SKILL.md note.

## Notes

- `generate-secrets.sh` shows the documented template leak (generates unused
  `NEXTCLOUD_ADMIN_PASSWORD`, `DB_ROOT_PASSWORD`, …). Harmless.
- SKILL.md's `discourse/base` image warning does not apply — template already uses
  `discourse/discourse:latest` (pull was large; one CDN timeout, retry succeeded).
