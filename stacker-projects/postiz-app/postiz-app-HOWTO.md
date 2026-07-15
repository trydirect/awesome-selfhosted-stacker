# Postiz App — Stacker Deploy HOWTO

Six containers: app (ghcr.io/gitroomhq/postiz-app:latest) + postgres:17-alpine + redis:7.2 + elasticsearch:7.17.27 + postgres:16 + temporalio/auto-setup:1.28.1.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Verify

```bash
curl -I http://<SERVER_IP>:4007/
```

## Notes

- Port: 4007 (maps to container port 5000)
- Temporal on localhost:7233
- Postgres for app + separate Postgres for Temporal
- File bind mount: `./dynamicconfig/development-sql.yaml` is bundled and deployed
- Named volumes: postiz_config, postiz_uploads, postiz_postgres_data, postiz_redis_data, temporal_elasticsearch_data, temporal_postgres_data
