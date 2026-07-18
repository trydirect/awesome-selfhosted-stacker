# Mattermost — Stacker Deploy HOWTO

Two containers: `mattermost/mattermost-enterprise-edition:latest` + `postgres:16-alpine`. Team chat (alternative to Slack).

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

Open `http://<SERVER_IP>:8065/` in a browser.

Create an admin account on first visit.

## Notes

- Port: 8065
- Database: postgres:16-alpine
- Data: `mattermost_data`, `mattermost_logs`, `mattermost_plugins` volumes
- Supports file sharing, integrations, webhooks
