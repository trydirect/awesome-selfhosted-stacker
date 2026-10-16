# scriberr — known issues

## [BUG] First boot fills the disk with whisperX env/models; SQLite crash-loops

**Severity:** High (deploy "succeeds" but the app never starts)
**Date:** 2026-10-16

### Steps
1. `stacker deploy --target server` to the 2 GB / 38 GB-disk test server
   (26 GB free before deploy) — deployment #1374 reported **completed**.
2. `project-app-1` restart-loops.

### Actual
```
level=ERROR msg="Failed to connect to database"
error="failed to connect to database: database or disk is full (13)"
```
Server disk went 26 GB free → **100% full** during first boot: the image
(whisperX-based) plus first-run downloads into the `scriberr_data` /
`scriberr_env` volumes consume tens of GB. Once the disk filled, SQLite
failed and the app crash-looped.

### Additional finding
Deployment #1374 was marked `✓ completed` by the platform while the app was
restart-looping — the deploy watch did not catch the failure (same family as
the watch-verdict bugs in root BUGS.md).

### Resource floor (test result)
- Needs a large disk: **≥40 GB free recommended** (observed 26 GB insufficient).
- After cleanup (`compose down --volumes`, image prune) the disk stayed at
  81% until further pruning.

### Status
Not verified working — skipped on this test server; retest on a large-disk
host (or local Docker once sorted) and report.
