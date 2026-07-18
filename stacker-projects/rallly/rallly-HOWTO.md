# Rallly — Stacker Deploy HOWTO

Two containers: `lukevella/rallly:latest` + `postgres:16-alpine`. Date scheduling polls.

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

## Notes

- Port: 3000
- Database: postgres:16-alpine
- Alternative to Doodle
