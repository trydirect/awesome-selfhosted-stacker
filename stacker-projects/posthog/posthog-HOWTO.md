# PostHog — Stacker Deploy HOWTO

Product analytics platform. Three containers (app + postgres + redis).

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
curl -I http://<SERVER_IP>:8000/
```

## Notes

- Port: 8000
- postgres on localhost:5432, redis on localhost:6379
- Named volumes: posthog_db, posthog_redis
