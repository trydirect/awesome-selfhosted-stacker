# Outline — Stacker Deploy HOWTO

Three containers: app (outlinewiki/outline:latest) + postgres:16 + redis:7-alpine.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Troubleshooting

### PostgreSQL version mismatch

If a previous deploy used PG15, the volume will be incompatible with PG16.
Remove the stale volume and redeploy:

```bash
ssh root@<SERVER_IP> "docker rm -f project-app-1 project-postgres-1 project-redis-1"
ssh root@<SERVER_IP> "docker volume rm -f project_postgres_data"
stacker deploy --target server
```

### Migrations

Outline runs DB migrations on container startup (via entrypoint). The `post_deploy` hook
(`.stacker/migrate.sh`) runs `npx sequelize db:migrate` but fails because `npx` is not
in the container PATH — this is harmless since migrations already run on startup.

## Verify

```bash
curl -I http://<SERVER_IP>:3000/
```

## Notes

- Port: 3000
- postgres on localhost:5432, redis on localhost:6380
- Set `URL` and `COLLABORATION_URL` in `.env` to the app's public URL for SSO/webhook features
- Named volumes: postgres_data
