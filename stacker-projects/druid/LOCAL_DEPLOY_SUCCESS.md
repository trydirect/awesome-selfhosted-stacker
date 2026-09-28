# druid — Local Deploy Success

**Date:** 2026-09-28
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

## Fixture fixes applied (pre-approved class — see `BUGS.md`)

1. **Port range expanded** (`"8100-8105:8100-8105"` → six discrete `"8100:8100"`…`"8105:8105"`
   pairs) — works around the stacker port-range preflight false positive (root `BUGS.md`:
   `TcpListener::bind("0.0.0.0:8100-8105")` always errors → always "occupied").
2. **`druid_extensions_loadList: '["postgresql-metadata-storage"]'`** added to the five
   druid services (router, coordinator, broker, historical, middlemanager) — the
   `micro-quickstart` profile defaults to Derby only and the postgres metadata
   connector failed with `Unknown provider [postgresql] … known options [[derby]]`.
   Extension dir name is `postgresql-metadata-storage` (connector type stays
   `postgresql`).

## Commands

```bash
cd stacker-projects/druid
./scripts/generate-secrets.sh
set -a; source ../../.env; set +a
stacker config validate                  # ✓ valid
stacker deploy --target local --force-rebuild
```

## Verification

| Check | Result |
|---|---|
| Containers | all 7 Up, stable: app (router 8888), coordinator, broker, historical, middlemanager (8091+8100-8105), postgres (healthy), zookeeper |
| HTTP `GET /` (router) | **200** |
| Rendered loadList | `druid_extensions_loadList: "[\"postgresql-metadata-storage\"]"` — clean (the documented serde_yaml quoting bug did NOT trigger on this path) |

## Notes

- `apache/druid:31.0.0` is amd64-only (emulated locally; runs fine).
- Pre-flight quirk: after a compose change the port-conflict check flagged the
  project's *own* still-running middlemanager ports (the own-container exclusion
  missed them) — `docker compose -p druid down` cleared it.
- The documented `DRUID_EXTENSIONS_LOADLIST` serde_yaml round-trip bug
  (`'"[\"druid-avro\"]"'` corruption) did not appear — the generator emitted a
  correctly escaped value on first render.
