# vane — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `itzcrazykns1337/vane:v1.12.2`, port 3000)

## Commands

```bash
cd stacker-projects/vane
./scripts/generate-secrets.sh     # no secrets needed
stacker deploy --target local
```

## Verification (after healthcheck fix)

- `docker ps` → `vane-app-1 Up (healthy) 0.0.0.0:3000->3000/tcp`
- `curl http://localhost:3000/` → HTTP 200, Next.js UI HTML served
  (Perplexica successor / vane v1.12.2)

## Fix applied

- First deploy left the container `unhealthy`: the app binds only to the
  container eth0 IP, so `curl http://localhost:3000/` inside the healthcheck
  always failed (see BUGS.md).
- Healthcheck changed to `CMD-SHELL curl -fs http://$(hostname):3000/` —
  re-deploy confirms `Up (healthy)`.

## Notes

- CLI printed the known `✗ Timeout waiting for containers` false-negative
  (root BUGS.md:1063).
- Teardown: `stacker destroy -y`; project image removed afterwards
  (`docker rmi itzcrazykns1337/vane:v1.12.2`).
