# Grafana — Stacker Deploy HOWTO

Single container: `grafana/grafana:latest`. Monitoring dashboards and observability.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:3000/` in a browser.

Login with `admin` / password from `.env`.

## Notes

- Port: 3000
- Data: `grafana_data` volume
- Supports Prometheus, InfluxDB, Elasticsearch, MySQL, PostgreSQL data sources
- Hundreds of community dashboards available
