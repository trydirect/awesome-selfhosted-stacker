# [BUG] plane AIO requires S3 + AMQP env (DOMAIN_NAME/AMQP_URL/AWS_*)

## Status: BLOCKED

## Summary
makeplane/plane-aio-community requires a long list of env vars at boot:
DOMAIN_NAME, AMQP_URL, AWS_REGION, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY,
AWS_S3_BUCKET_NAME. Missing any causes an immediate exit.

## Root cause
Plane's AIO image assumes an external S3-compatible store and an AMQP broker.
There is no embedded/minio-only mode.

## Expected
App boots with minimal config.

## Actual
\`❌ 'DOMAIN_NAME' is not set or is empty\` (and 5 more), container restarts.

## Workaround
Deploy with a full MinIO + RabbitMQ stack and all AWS_* env vars. Too many
moving parts for a single stacker.yml; needs a multi-service compose.

## Reproduction
```bash
cd stacker-projects/plane
./scripts/generate-secrets.sh
stacker deploy --target server --server-host 46.224.127.228 --server-user root --server-ssh-key ../../stacker-project-test
```

## Environment
- Test server: 46.224.127.228
- Logged: 2026-10-10
