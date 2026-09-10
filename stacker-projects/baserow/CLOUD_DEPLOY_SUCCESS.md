# Baserow — Cloud Deploy Success

**Date:** 2026-09-10
**Server:** 116.202.19.183 (Hetzner, fsn1, cpx22)
**Deployment:** #285 — status: completed

## Deploy Command

```bash
cd stacker-projects/baserow
./scripts/generate-secrets.sh
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN /Users/vasilipascal/work/stacker-project-examples/.env | cut -d= -f2 | awk '{print $1}')
stacker deploy --target cloud --force-new
```

## Access

- **Web UI:** http://116.202.19.183:80

## Verification

```
$ curl -s http://116.202.19.183:80/_health/ | head -1
<!DOCTYPE html>...<title>Baserow | Baserow</title>
```
