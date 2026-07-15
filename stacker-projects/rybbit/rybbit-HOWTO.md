# Rybbit — Stacker Deploy HOWTO

Analytics platform. Five containers (app + backend + clickhouse + postgres + redis).

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
curl -I http://<SERVER_IP>:3002/   # app (Next.js UI)
curl -I http://<SERVER_IP>:3001/   # backend API
```

## Notes

- App port: 3002, Backend port: 3001
- Named volumes: rybbit_clickhouse_data, rybbit_postgres_data, rybbit_redis_data
- Config bundle includes clickhouse config XML files from `./clickhouse/config.d/`
- MAPBOX_TOKEN needs to be set manually in .env for map features
