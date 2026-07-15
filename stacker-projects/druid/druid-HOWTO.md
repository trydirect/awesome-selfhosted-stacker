# Druid — Stacker Deploy HOWTO

Eight containers: router (app) + postgres + zookeeper + coordinator + broker + historical + middlemanager. All use `apache/druid:31.0.0`.

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
curl -s http://<SERVER_IP>:8888/status
```

## Notes

- Port: 8888 (router), 8091 (middlemanager), 8100-8105 (middlemanager tasks)
- postgres on localhost:5432, zookeeper on localhost:2181
- Template used `apache/druid:38.0.0` which doesn't exist — use 31.0.0 instead
- Named volumes: druid_metadata_data, druid_zookeeper_data/datalog, druid_shared, *\_var per service
- Relies on `druid_extensions_loadList` env var (JSON array) — serde_yaml 0.9 round-trip breaks quoting; set via runtime.properties instead if custom extensions are needed
