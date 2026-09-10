# CrowdSec — Cloud Deploy Success

**Date:** 2026-09-10
**Server:** 116.202.19.183 (Hetzner, fsn1, cpx22)
**Deployment:** #287 — status: completed

## Deploy Command

```bash
cd stacker-projects/crowdsec
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN /Users/vasilipascal/work/stacker-project-examples/.env | cut -d= -f2 | awk '{print $1}')
stacker deploy --target cloud --force-new
```

## Notes

CrowdSec is a background security service — no web UI. Runs as a Docker container collecting and analyzing logs.
