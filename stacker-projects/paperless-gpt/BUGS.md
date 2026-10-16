# paperless-gpt — known issues

## [BUG] Image tag `ghcr.io/paperless-ngx/paperless-ngx:v3.3.1` does not exist (404)

**Severity:** High (deploy fails at image pull — stack cannot start)
**Date:** 2026-10-16
**Status:** suggested fix, NOT applied (pending approval)

### Steps
1. `stacker deploy --target local` in this directory.

### Actual
```
Error response from daemon: failed to resolve reference
"ghcr.io/paperless-ngx/paperless-ngx:v3.3.1": not found
```
`docker manifest inspect` results:
- `ghcr.io/paperless-ngx/paperless-ngx:v3.3.1` → missing
- `ghcr.io/paperless-ngx/paperless-ngx:3.3.1` → EXISTS
- `ghcr.io/paperless-ngx/paperless-ngx:v3.3.0` → missing
- `ghcr.io/paperless-ngx/paperless-ngx:2.13.5` / `:latest` → EXISTS
- Other template images are fine: `icereed/paperless-gpt:v0.31.0` (with `v`
  prefix — correct for this repo), `postgres:18-alpine`, `redis:7-alpine`

### Root cause
paperless-ngx publishes GHCR tags **without** the `v` prefix; the template
uses `v3.3.1`.

### Suggested fix (template)
```yaml
  - name: paperless
    image: ghcr.io/paperless-ngx/paperless-ngx:3.3.1
```
Not applied — template left unmodified pending approval. Local deploy not
performed (aborted at pull).
