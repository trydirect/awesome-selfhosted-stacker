# localagi — known issues

## [NOTE] Not deployable on the 2 GB test server — LocalAI pre-loads LLM models

**Severity:** Low (template itself is plausible; test infra too small)
**Date:** 2026-10-16

### Finding
The `localai` service command pre-loads `gemma-3-4b-it-qat` +
`granite-embedding-107m-multilingual` at startup (model downloads into the
`models` volume, then multi-GB RAM at load). The host is a shared 2 GB test
server (~1.3 GB free) — deploying would OOM-kill unrelated platform services
(statuspanel, caddy) on the same host.

A local (Docker Desktop) pull attempt also hit the Docker VM disk-read-only
crash before completion.

### Resource floor (test result)
- RAM: ≥8 GB (LocalAI + 4B model), disk: ≥20 GB (models)
- Untested; retest on a larger host when available.
