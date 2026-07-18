# Typebot — Stacker Deploy HOWTO

Two containers: `baptistearno/typebot-builder:latest` + `postgres:16-alpine`. Conversational form builder (alternative to Typeform).

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

Open `http://<SERVER_IP>:3001/` in a browser.

## Notes

- Port: 3001
- Database: postgres:16-alpine
- Create forms, chatbots, and conversational flows visually
- Embed typebots on any website
