# Manticore Search — Cloud Deploy Success

**Date:** 2026-09-10
**Server:** 2.28.16.187 (Hetzner, fsn1, cpx22)
**Deployment:** #289 — status: completed

## Deploy Command

```bash
cd stacker-projects/manticore
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN /Users/vasilipascal/work/stacker-project-examples/.env | cut -d= -f2 | awk '{print $1}')
stacker deploy --target cloud --force-new
```

## Access

- **HTTP API:** http://2.28.16.187:9308

## Verification

```
$ curl -s -o /dev/null -w '%{http_code}' http://2.28.16.187:9308/
200
```
