# bolt.diy — known issues

## [BUG] Upstream Docker image is broken: `vite: not found` crash-loop

**Severity:** High (template cannot start as configured)
**Date:** 2026-10-16
**Status:** upstream image bug — not a stacker.yml issue

### Steps
1. `stacker deploy --target local` in this directory (image
   `ghcr.io/stackblitz-labs/bolt.diy:latest`, built 2026-10-08).
2. Container `bolt-diy-app-1` starts and immediately crash-loops.

### Actual
```
> bolt@1.0.0 dockerstart /app
> vite preview --host 0.0.0.0 --port 5173 --strictPort

sh: 1: vite: not found
ELIFECYCLE  Command failed.
```
- `:latest`: `/app/node_modules/.bin/` contains only cf-wrangler, dotenv,
  eslint, isogit, mime, wrangler, wrangler2 — **no vite at all**.
- `:main` (alternative tag, version 1.0.0): same crash, same `vite: not found`.
- The image's CMD is `pnpm run dockerstart` → `vite preview ...`; vite is
  evidently pruned from node_modules at image build time.

### Expected
Container starts and answers `GET /api/health` (template healthcheck).

### Workaround / fix options
- No working GHCR tag found (`:latest`, `:main` both broken as of 2026-10-16).
- Possible future fix: build from source (`app.dockerfile`) or override the
  container command to `pnpm install --dev && pnpm run dockerstart` (heavy,
  needs network at every start) — neither applied, template left as-is
  pending upstream fix.

### Verification performed
- `stacker deploy --target local` → "Timeout waiting for containers"
- `docker logs bolt-diy-app-1` → crash-loop as above
- `curl http://localhost:5173/api/health` → connection refused
- Teardown: `stacker destroy -y` OK; project images removed afterwards.
