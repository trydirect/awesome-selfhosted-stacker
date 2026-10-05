# ampache — LOCAL deploy SUCCESS

**Date:** 2026-10-05
**Stacker:** v0.3.4 (ccd7184) — with compose env-alias fix `990b6976`

## Command

```bash
cd stacker-projects/ampache
stacker deploy --target local
```

## Verification

- `ampache-mysql-1` Up (healthy), `ampache-app-1` Up
- `curl http://127.0.0.1:8080/` → **302** (Ampache web UI)
- `stacker destroy -y` → ✓ Stack destroyed successfully

## Fix verified

Stacker `990b6976` (env_reference_aliases) resolves the `${DB_PASSWORD}` → `${MYSQL_PASSWORD}`
rewrite that previously caused mysql crash-loops. Generated compose now references
`DB_PASSWORD` / `DB_ROOT_PASSWORD` — matching `.env`.
