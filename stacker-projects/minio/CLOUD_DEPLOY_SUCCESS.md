# MinIO — Cloud Deploy Success

**Date:** 2026-09-05
**Server:** 23.88.120.136 (Hetzner, fsn1, cpx22)
**Deployment:** #278 — status: completed

## Deploy Command

```bash
cd stacker-projects/minio
./scripts/generate-secrets.sh
export HCLOUD_TOKEN=$(grep CLOUD_API_TOKEN /Users/vasilipascal/work/stacker-project-examples/.env | cut -d= -f2 | awk '{print $1}')
stacker deploy --target cloud --force-new
```

## Access

- **Console:** http://23.88.120.136:9001
- **S3 API:** http://23.88.120.136:9000
- **Login:** admin / (password in `.env` as `MINIO_ROOT_PASSWORD`)

## Verification

```
$ curl -s -o /dev/null -w '%{http_code}' http://23.88.120.136:9001/
200
```
