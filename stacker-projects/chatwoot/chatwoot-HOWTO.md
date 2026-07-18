# Chatwoot — Stacker Deploy HOWTO

Three containers: `chatwoot/chatwoot:develop-ce` + `postgres:16-alpine` + `redis:7-alpine`. Customer support platform (alternative to Intercom, Zendesk).

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

Create an admin account on first visit.

## Notes

- Port: 3000
- Database: postgres:16-alpine
- Redis for caching and real-time features
- Supports website live chat, email, WhatsApp, Telegram, SMS
- REST API + webhooks for integrations
