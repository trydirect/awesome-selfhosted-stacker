# s4core — Stacker Deploy HOWTO

S3-compatible object storage server with a web console. Two containers (s4core + s4console), no external DB.

## Prerequisites

- Stacker v0.3.0+ authenticated
- SSH key for server

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
curl -I http://<SERVER_IP>:9000/health   # s4core API
curl -I http://<SERVER_IP>:3000/          # s4console web UI
```

Both should return HTTP 200.

## Notes

- API port: 9000, Console port: 3000
- Named volumes: `s4_data`
