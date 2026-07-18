# Automatisch — Stacker Deploy HOWTO

Two containers: `automatisch/automatisch:latest` + `postgres:16-alpine`. Workflow automation (alternative to Zapier).

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

Create an account on first visit.

## Notes

- Port: 3000
- Database: postgres:16-alpine
- Supports webhooks, scheduled triggers, and 100+ app integrations
- No vendor lock-in, fully self-hosted
