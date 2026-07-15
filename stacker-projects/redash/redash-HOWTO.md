# Redash — Stacker Deploy HOWTO

Three containers: app (redash/redash:latest) + postgres:16-alpine + redis:7-alpine.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Workaround: remote_user Ansible error

If the Stacker server pauses with `[WARNING]: Found variable using reserved name: remote_user`,
the app container is created but not started. Start it manually:

```bash
ssh root@<SERVER_IP> "docker start project-app-1"
```

## Verify

```bash
curl -I http://<SERVER_IP>:5000/
```

## Notes

- Port: 5000
- postgres on localhost:5432, redis on localhost:6379
- Named volumes: redash_db, redash_redis
