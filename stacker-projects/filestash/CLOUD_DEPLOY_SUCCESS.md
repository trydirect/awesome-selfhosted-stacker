# Filestash — Cloud Deploy Success

**Date:** 2026-09-10
**Server:** 159.69.114.230 (Hetzner, fsn1, cpx22)
**Deployment:** #288 — status: completed

## Deploy Command

```bash
cd stacker-projects/filestash
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN /Users/vasilipascal/work/stacker-project-examples/.env | cut -d= -f2 | awk '{print $1}')
stacker deploy --target cloud --force-new
```

## Access

- **Web UI:** http://159.69.114.230:8334

## Verification

```
$ curl -s -L -o /dev/null -w '%{http_code}' http://159.69.114.230:8334/
200
```
