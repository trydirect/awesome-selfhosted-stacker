# open-notebook — known issues

## [BUG] surrealdb crash-loops: Permission denied on root-owned named volume

**Severity:** High (stack could not start — app waited for DB forever)
**Date:** 2026-10-16
**Status:** FIXED 2026-10-16 — volume moved to `/home/nonroot`

### Summary
`surrealdb/surrealdb:v2` runs as UID 65532 (all v2 tags: v2, v2.3.7, v2.2.1,
v2.1.0). A named volume mounted at `/mydata` is seeded root:root →
`Failed to create RocksDB directory: PermissionDenied` crash-loop.

### What did NOT work
- `cap_add: ["DAC_OVERRIDE"]` — Docker does not put added capabilities into
  the effective set for non-root container processes here (isolated test:
  `docker run --user 65532 --cap-add DAC_OVERRIDE alpine mkdir /etc/x` →
  still denied). Upstream's own fix is `user: root`, which the stacker.yml
  schema cannot express for `services[]` (only `app.user` exists; the compose
  generator already has `ComposeService.user` — a small core gap).

### Fix that works within the current schema
The image ships `/home/nonroot` owned by 65532:65532. Docker named-volume
copy-up seeds the volume with that directory's ownership, so:

```yaml
  - name: surrealdb
    image: surrealdb/surrealdb:v2
    command: start --log info --user ${SURREAL_USER} --pass ${SURREAL_PASSWORD} rocksdb:/home/nonroot/mydatabase.db
    volumes:
      - open_notebook_surreal:/home/nonroot
```

Verified: `open-notebook-surrealdb-1 Up`, app `/health` →
`{"status":"healthy"}`, UI on 8502 answers 307 (login redirect).

### Evidence (pre-fix)
- `docker logs open-notebook-surrealdb-1` → PermissionDenied crash-loop
- image export: `home/nonroot/` = `drwx------ 65532 65532`
- volume ownership test: mount at `/home/nonroot` → 65532:65532; at
  `/mydata` → 0:0
