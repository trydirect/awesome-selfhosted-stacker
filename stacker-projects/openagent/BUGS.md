# openagent — known issues

## [BUG] mysql:8.0.25 has no arm64 manifest

**Severity:** Low (x86_64 servers unaffected); blocked local/arm64 deploys
**Date:** 2026-10-16
**Status:** FIXED 2026-10-16 — pinned `mysql:8.0.43`

### Summary
`mysql:8.0.25` publishes amd64 only; pull failed on Apple Silicon with
`no matching manifest for linux/arm64/v8`. The app image
(`casbin/openagent:2.95.1`) is multi-arch and fine.

### Fix
```yaml
  - name: db
    image: mysql:8.0.43   # multi-arch (amd64+arm64); 8.0.25 was amd64-only
```
Verified: full local deploy healthy, `/api/health` → `{"status":"ok"}`.

### Fix options considered
- `mysql:8.0` (floating) — multi-arch but unpinned; 8.0.43 pin preferred.
