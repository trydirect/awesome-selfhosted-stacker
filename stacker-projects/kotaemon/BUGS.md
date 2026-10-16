# kotaemon — known issues

## [SEC] Open RCE #844 / IDOR #846 — self-host only, never expose publicly

**Status:** upstream security caveat (from the quick-deploy targets list).
Do **not** submit this template to the marketplace until upstream fixes
https://github.com/Cinnamon/kotaemon/issues/844 and related IDOR #846.

## [NOTE] Not deployable on the 2 GB test server — Elasticsearch-heavy

**Severity:** Low (template itself is plausible; test infra too small)
**Date:** 2026-10-16

### Finding
The stack includes Elasticsearch (RAM-hungry, ~1 GB+ at startup) — exceeds
the shared 2 GB test server (~1.3 GB free); deploying would OOM unrelated
platform services on the host.

### Resource floor (test result)
- RAM: ≥6 GB (ES + app + models), disk: ≥20 GB
- Untested; retest on a larger host when available — and only after the
  upstream security fixes.
