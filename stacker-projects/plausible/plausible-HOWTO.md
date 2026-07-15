# Plausible — Stacker Deploy HOWTO

Privacy-friendly analytics. Three containers (app + postgres + clickhouse).

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
Expected: HTTP 302 (redirect to login)

## Notes

- Port: 8000
- Uses custom compose file: `docker/production/compose.yml`
- Config bundle includes `.deploy-config/init-clickhouse.sql`
- postgres on `plausible_db:5432`, clickhouse on `plausible_events_db:8123`
- Named volumes: db_data, event_data, event_logs, plausible_data
