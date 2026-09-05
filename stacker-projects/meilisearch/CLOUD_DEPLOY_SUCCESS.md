# Meilisearch — Cloud Deploy Success

**Date:** 2026-09-05
**Server:** 188.245.118.5 (Hetzner, fsn1, cpx22)
**Deployment:** #277 — status: completed

## Deploy Command

```bash
cd stacker-projects/meilisearch
./scripts/generate-secrets.sh
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN /Users/vasilipascal/work/stacker-project-examples/.env | cut -d= -f2 | awk '{print $1}')
stacker deploy --target cloud --force-new
```

## Access

- **Web UI:** http://188.245.118.5:7700
- **Health:** http://188.245.118.5:7700/health

## Verification

```
$ curl -s http://188.245.118.5:7700/health
{"status":"available"}

$ curl -s -o /dev/null -w '%{http_code}' http://188.245.118.5:7700/
200
```
