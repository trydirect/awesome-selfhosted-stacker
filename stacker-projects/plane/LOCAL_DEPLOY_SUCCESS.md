# Plane — Local Deploy Success

## Result: SUCCESS

- **Image:** `makeplane/plane-aio-community` (AIO, container port 80)
- **Host port:** 8000
- **Deployments:** #1348
- **Verified:** HTTP 200

## Fix applied

The AIO image needs a full data stack + env at boot. Added:
- `mq` service — `rabbitmq:3.13-alpine` (user `plane`, vhost `plane`).
- `minio` service — `bitnamilegacy/minio:latest` (`minio/minio` was removed from
  Docker Hub), fixed creds, `MINIO_DEFAULT_BUCKETS=uploads`, volume
  `/bitnami/minio`, healthcheck on `:9000/minio/health/live`.
- Env: `DOMAIN_NAME=localhost`, `DATABASE_URL`, `AMQP_URL`,
  `AWS_S3_ENDPOINT_URL=http://minio:9000`, `SECRET_KEY`.
- Port mapped `8000:80` (AIO listens on :80).

## Commands used
```bash
cd stacker-projects/plane
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 \
  --server-user root --server-ssh-key ../../stacker-project-test --force-rebuild
```

## Verification
- `curl -o /dev/null -w "%{http_code}" http://46.224.127.228:8000/` → `200`.
- 5/5 containers healthy; title "Plane | Simple, extensible...".

## Environment
- Test server: 46.224.127.228
- Date: 2026-10-11
