# AdGuard Home — Cloud Deploy Success

**Date:** 2026-09-13
**Server:** 116.202.19.183 (Hetzner, fsn1, cpx22)
**Deployment:** #303 — status: completed

## Deploy Command

```bash
cd stacker-projects/adguard-home
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN /Users/vasilipascal/work/stacker-project-examples/.env | cut -d= -f2 | awk '{print $1}')
stacker deploy --target cloud --force-new
```

## Access

- **Web UI:** http://116.202.19.183:3000
- **DNS:** 116.202.19.183:8053 (TCP/UDP)

## Verification

```
$ curl -s -L -o /dev/null -w '%{http_code}' http://116.202.19.183:3000/
200
```

## Notes

- Port 53 mapped to 8053 on host (systemd-resolved uses 53)
- Fixed port conflict with systemd-resolved (same as pihole)
