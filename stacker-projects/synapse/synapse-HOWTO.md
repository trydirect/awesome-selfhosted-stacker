# Synapse — Stacker Deploy HOWTO

Matrix homeserver. Two containers (synapse + postgres).

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
curl -I http://<SERVER_IP>:8008/
```

## Notes

- Ports: 8008 (HTTP), 8448 (HTTPS federation)
- synpase needs initial config generation on first run (`SYNAPSE_SERVER_NAME` must be a valid domain)
- postgres on localhost:5432
- Named volumes: `synapse_data`, `synapse_db`
