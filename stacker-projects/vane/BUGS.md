# vane — known issues

## [BUG] Healthcheck failed: app binds only to container eth0 IP, not loopback

**Severity:** Medium (app worked, container stayed `unhealthy`)
**Date:** 2026-10-16
**Status:** FIXED 2026-10-16 — healthcheck now uses `http://$(hostname):3000/`

### Summary
The image's Next.js server binds to the hostname/eth0 interface only:
`127.0.0.1:3000` and `[::1]:3000` are refused inside the container while
`http://$(hostname):3000/` returns 200. The original healthcheck
`curl -fs http://localhost:3000/` therefore always exited 7 and the
container stayed `unhealthy` even though the app served HTTP 200 through
docker-proxy.

### Fix
```yaml
healthcheck:
  test: "CMD-SHELL curl -fs http://$(hostname):3000/"
```
Re-deploy verified: `vane-app-1 Up (healthy)`.

### Evidence (pre-fix)
- `docker inspect .State.Health.Log` → repeated ExitCode 7
- `docker exec ... curl http://$(hostname):3000/` → 200
