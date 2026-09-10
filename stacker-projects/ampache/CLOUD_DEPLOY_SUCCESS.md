# Ampache — Cloud Deploy Success

**Date:** 2026-09-10
**Server:** 116.202.19.183 (Hetzner, fsn1, cpx22)
**Deployment:** #283 — status: completed

## Deploy Command

```bash
cd stacker-projects/ampache
./scripts/generate-secrets.sh
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN /Users/vasilipascal/work/stacker-project-examples/.env | cut -d= -f2 | awk '{print $1}')
stacker deploy --target cloud --force-new
```

## Access

- **Web UI:** http://116.202.19.183:8080

## Verification

```
$ curl -s -L -o /dev/null -w '%{http_code}' http://116.202.19.183:8080/
200
```
