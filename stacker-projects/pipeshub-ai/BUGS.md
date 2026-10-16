# pipeshub-ai — known issues

## [NOTE] Not deployable on the 2 GB test server — 5-service stack (mongo, neo4j)

**Severity:** Low (template itself is plausible; test infra too small)
**Date:** 2026-10-16

### Finding
The slim subset is mongo + redis + qdrant + neo4j + app. Neo4j alone wants
~1 GB at startup and the full set exceeds the shared 2 GB test server
(~1.3 GB free); deploying would OOM unrelated platform services on the host.

### Resource floor (test result)
- RAM: ≥6 GB, disk: ≥20 GB
- Untested; retest on a larger host when available.
