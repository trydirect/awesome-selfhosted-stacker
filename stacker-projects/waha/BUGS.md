# waha — known issues

## [BUG] Cannot run locally on Apple Silicon: image has no arm64 manifest

**Severity:** Low for x86_64 servers (template target); blocks local test on arm64
**Date:** 2026-10-16

### Steps
1. `stacker deploy --target local` on macOS/arm64 (image
   `devlikeapro/waha:latest-2026.9.2`).

### Actual
```
Error: ... no matching manifest for linux/arm64/v8 in the manifest list
```
`docker manifest inspect devlikeapro/waha:latest` and
`devlikeapro/waha:latest-2026.9.2` list only `amd64` (+ attestation) — no
arm64 build for any tag checked.

### Expected
Image pulls and container starts (as it will on x86_64 targets).

### Impact / workaround
- Template is deployable to Hetzner/cloud/server (x86_64) — this is a
  local-test limitation only.
- No local verification performed: no container, no health check. `stacker
  destroy`/image cleanup not required (pull failed before container create).

### Fix options
- Upstream arm64 build request, or
- `platform: linux/amd64` (emulation) in the generated compose — slow
  Chromium-based WhatsApp engine under qemu; not applied.
