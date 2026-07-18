# Directus — Stacker Deploy HOWTO

Two containers: `directus/directus:latest` + `postgres:16-alpine`. Headless CMS with REST and GraphQL API.

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

Open `http://<SERVER_IP>:8055/admin` in a browser.

Login with credentials from `.env`.

## Notes

- Port: 8055
- Database: postgres:16-alpine
- Auto-generates REST and GraphQL API for any SQL database
- No-code admin dashboard for content management
