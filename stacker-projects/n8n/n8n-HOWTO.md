# n8n — Stacker Deploy HOWTO

Two containers: `n8nio/n8n:latest` + `postgres:16-alpine`. Workflow automation (alternative to Zapier).

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

Open `http://<SERVER_IP>:5678/` in a browser.

Login with credentials from `.env`.

## Notes

- Port: 5678
- Database: postgres:16-alpine
- Data: `n8n_data` volume
- Supports 400+ integrations (Slack, GitHub, Stripe, etc.)
