# [FIXED] plane AIO requires S3 + AMQP env (DOMAIN_NAME/AMQP_URL/AWS_*)

## Status: FIXED / VERIFIED

## Summary
`makeplane/plane-aio-community` requires a long list of env vars at boot
(DOMAIN_NAME, AMQP_URL, AWS_REGION/KEY/SECRET/BUCKET). Missing any causes an
immediate exit.

## Resolution (2026-10-11)
Deployed the full multi-service stack plane needs:
- `mq` — `rabbitmq:3.13-alpine` (user `plane`, vhost `plane`).
- `minio` — `bitnamilegacy/minio:latest` (note: `minio/minio` was removed from
  Docker Hub), fixed creds, `MINIO_DEFAULT_BUCKETS=uploads`, `/bitnami/minio`
  volume, healthcheck on `:9000/minio/health/live`.
- Env: `DOMAIN_NAME=localhost`, `DATABASE_URL`, `AMQP_URL`,
  `AWS_S3_ENDPOINT_URL=http://minio:9000`, `SECRET_KEY`.
- Port `8000:80` (AIO listens on :80).

Result: HTTP 200 on :8000, 5/5 containers healthy. See
`LOCAL_DEPLOY_SUCCESS.md`.

## Environment
- Test server: 46.224.127.228
- Deployment: #1348
