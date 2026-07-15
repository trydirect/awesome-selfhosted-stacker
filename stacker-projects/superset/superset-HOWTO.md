# Superset — Stacker Deploy HOWTO

Three containers: app (apache/superset:latest) + postgres:16-alpine + redis:7-alpine.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## First-run setup

Superset needs an admin user created on first deploy:

```bash
ssh root@<SERVER_IP> "docker exec -it project-app-1 superset fab create-admin"
ssh root@<SERVER_IP> "docker exec project-app-1 superset db upgrade"
ssh root@<SERVER_IP> "docker exec project-app-1 superset init"
```

## Verify

```bash
curl -I http://<SERVER_IP>:8088/
```

## Notes

- Port: 8088
- postgres on localhost:5432, redis on localhost:6379
- Named volumes: superset_db, superset_redis
