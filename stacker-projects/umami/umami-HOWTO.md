# umami — Stacker Deploy HOWTO

Privacy-focused analytics. Two containers (umami app + postgres).

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
curl -I http://<SERVER_IP>:3000/
```
Expected: HTTP 200

## Notes

- App port: 3000
- postgres on localhost:5432 (not exposed externally)
- Named volumes: `postgres_data`
