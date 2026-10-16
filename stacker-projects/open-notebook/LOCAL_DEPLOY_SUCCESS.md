# open-notebook — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `lfnovo/open_notebook:1.15.0`, ports 8502+5055,
surrealdb:surrealdb:v2)

## Commands

```bash
cd stacker-projects/open-notebook
./scripts/generate-secrets.sh     # SURREAL_USER/PASSWORD, OPEN_NOTEBOOK_*
stacker deploy --target local
```

## Verification (after surrealdb volume fix)

- `docker ps` → `open-notebook-app-1 Up (healthy) :8502,:5055`,
  `open-notebook-surrealdb-1 Up`
- `curl http://localhost:5055/health` → `{"status":"healthy"}`
- `curl http://localhost:8502/` → HTTP 307 (redirect to login UI)

## Fix applied

- First deploy crash-looped surrealdb (`PermissionDenied` on the root-owned
  named volume; image runs as UID 65532). `cap_add: DAC_OVERRIDE` did NOT
  help — Docker does not apply added capabilities to non-root processes in
  this runtime (verified with an isolated test).
- Working fix: mount the volume at `/home/nonroot` (exists in the image owned
  by 65532, so Docker's volume copy-up seeds the volume with that ownership)
  and point RocksDB at `rocksdb:/home/nonroot/mydatabase.db`. This is upstream
  `open_notebook` compose's intent (`user: root`) expressed within the current
  stacker.yml schema. See BUGS.md.

## Notes

- Teardown: `stacker destroy -y`; project images removed afterwards
  (`lfnovo/open_notebook:1.15.0`, `surrealdb/surrealdb:v2`).
