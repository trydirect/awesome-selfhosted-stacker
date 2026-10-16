# langchain-chatchat — known issues

## [NOTE] Not deployable on the 2 GB test server — xinference image is ~14 GB

**Severity:** Low (template itself is plausible; test infra too small)
**Date:** 2026-10-16

### Finding
The previously suspected "stale 2024 images" are **still published**:
- `chatimage/chatchat:0.3.1.3-93e2c87-20240829` → EXISTS (~1.9 GB compressed)
- `xprobe/xinference:v0.12.3` → EXISTS (~13.8 GB compressed, ~28 GB unpacked)

Deploy was **not attempted** on the shared 2 GB / 38 GB-disk test server: the
xinference image alone exceeds the available disk (7 GB free at decision
time), and xinference also loads models into RAM.

### Resource floor (test result)
- Disk: ≥60 GB free (images + models)
- RAM: ≥8 GB (xinference model serving)
- Untested; images pullable. Retest on a larger host when available.

### Note
Being 2024-era builds, expect possible runtime incompatibilities even on a
large host — record results when retested.
