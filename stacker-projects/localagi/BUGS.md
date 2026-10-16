# localagi — known issues

## [BUG] Pinned image `main-20261005225430` broken: `serve` command registered twice

**Severity:** High (app prints help and exits 0 in a restart loop)
**Date:** 2026-10-16
**Status:** FIXED 2026-10-16 — `image: quay.io/mudler/localagi:latest` +
required `LOCALAGI_MODEL`

### Summary
The rolling `main-*` builds (checked: 20261005225430, 20261016085029) register
the `serve` cobra command **twice** (root help lists it twice) — invoking
`serve` prints the subcommand help and exits 0 forever:

```
Start the LocalAGI web server with the agent pool and web UI.
Usage: local-agi serve [flags]
```

### What also matters
Working builds **panic at init** without `LOCALAGI_MODEL`:
```
panic: LOCALAGI_MODEL not set
```
The template env never set it — so even with a good image the app cannot
start.

### Fix applied
```yaml
  image: quay.io/mudler/localagi:latest      # Feb-2026 build; the only working tag
  environment:
    LOCALAGI_MODEL: "gemma-3-4b-it-qat"      # matches localai's preloaded model
```
Verified on cpx42: `project-app-1 Up (healthy)`, HTTP 302 on :8080,
localai `/readyz` OK, postgres healthy.

### Notes
- Quay publishes only rolling tags (`latest`, `main-YYYYMMDD…`, `sha-…`) — no
  versioned releases. `latest` currently points at a 2026-02-16 build while
  fresh `main-*` builds are broken. Pinning by digest
  (`@sha256:f50518…`) is the reproducible alternative if `latest` ever moves.
- `v2.8.0` / `v2.9.0` tags don't exist on quay (template `version: v2.9.0` is
  the stack version, not an image tag).
