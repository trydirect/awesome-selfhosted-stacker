# Discourse — Stacker Deploy HOWTO

Three containers: discourse (discourse/discourse:latest) + postgres with pgvector (pgvector/pgvector:0.8.0-pg16) + redis:7-alpine.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Post-deploy

```bash
# On first boot, Discourse compiles assets and runs DB migrations (2-5 min)
# Reset stale DB on re-deploy
docker compose -p project down -v
docker compose -p project up -d
```

## Access

Open `http://<SERVER_IP>:80/` in a browser. Register the first admin account.

## Notes

- Port: 80 (maps to container port 80)
- Uses `pgvector/pgvector:0.8.0-pg16` for PostgreSQL with pgvector extension
- Discourse runs its own internal nginx reverse proxy
- DB on localhost:5432, Redis on localhost:6379
- Named volumes: discourse_db, discourse_redis
- Configure SMTP via env vars before first boot to send emails
