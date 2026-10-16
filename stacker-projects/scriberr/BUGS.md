# scriberr — known issues

## [BUG] First boot fills small disks with whisperX env/models; SQLite crash-loops

**Severity:** High on small hosts (deploy "succeeds" but the app never starts)
**Date:** 2026-10-16
**Status:** verified working on cpx42 (301 GB disk) — see CLOUD_DEPLOY_SUCCESS.md

### Summary
On the 2 GB / 38 GB shared test server first boot filled the disk
(26 GB free → 100%) with whisperX env/model downloads into the
`scriberr_data` / `scriberr_env` volumes, then SQLite failed:

```
level=ERROR msg="Failed to connect to database"
error="failed to connect to database: database or disk is full (13)"
```
and the app crash-looped. Deployment #1374 was also marked `✓ completed` by
the platform while the app was restart-looping (watch-verdict gap).

### Resource floor (test result)
- Disk: **≥40 GB free recommended** (26 GB insufficient) — cpx42 (301 GB)
  completes first boot and reports healthy.
- Template `deploy.cloud.size` raised `cpx22` → `cpx42` accordingly.

### Verified (2026-10-16, cpx42)
`curl http://<server>:8080/health` → `{"status":"healthy","version":"1.0.0"}`,
root → 200, container `Up (healthy)`.
