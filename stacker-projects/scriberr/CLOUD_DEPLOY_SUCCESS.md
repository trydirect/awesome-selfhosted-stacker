# scriberr — cloud deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), target: fresh Hetzner cloud (cpx42, fsn1)
**Server:** scriberr-35d3 @ 167.233.196.133 (8 vCPU / 15 GiB / 301 GB disk)
**Template:** stacker.yml (ghcr.io/rishikanthc/scriberr:v1.2.0, port 8080)

## Commands

```bash
cd stacker-projects/scriberr
./scripts/generate-secrets.sh
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
# stacker.yml: deploy.cloud.size bumped cpx22 -> cpx42 (whisperX first-boot
# needs the disk/RAM; see BUGS.md for the 26 GB-fill incident on a 38 GB disk)
stacker deploy --target cloud --key htz-0 --force-new    # deployment #1375
```

## Verification

- `✓ Your SSH key authorized (...stacker-project-test.pub)` — SSH access
  confirmed before checks
- `docker ps` → `project-app-1 Up (healthy)` (plus platform `statuspanel`,
  `statuspanel_agent`)
- `curl http://167.233.196.133:8080/health` →
  `{"status":"healthy","version":"1.0.0"}`
- `curl http://167.233.196.133:8080/` → HTTP 200
- External port 8080 reachable (in `deploy.cloud.public_ports`)

## Notes

- Previous attempt on the 2 GB / 38 GB existing server filled the disk with
  whisperX env/models and crash-looped SQLite (see BUGS.md) — on cpx42
  (301 GB disk) first boot completes and the app is healthy.
- The `167.233.196.133` IP is recycled (an earlier deleted cpx42 had it) —
  known_hosts entry refreshed.
- Server left running (servers are never deleted); next heavy tests reuse it
  via `--target server --server-host 167.233.196.133`.
