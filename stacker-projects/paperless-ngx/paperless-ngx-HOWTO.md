# paperless-ngx — Stacker Deploy HOWTO

Document management system. Three containers (app + postgres + redis).

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
- The template uses `max_wal_level` in POSTGRES_INITDB_ARGS — the correct parameter is `wal_level`
- Named volumes: paperless_data, paperless_media, paperless_export, paperless_consume, paperless_db, paperless_redis
