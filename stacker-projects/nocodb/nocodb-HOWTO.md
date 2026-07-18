# NocoDB — Stacker Deploy HOWTO

Two containers: `nocodb/nocodb:latest` + `postgres:16-alpine`. Airtable alternative (no-code database).

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

Open `http://<SERVER_IP>:8080/` in a browser.

Create an account on first visit.

## Notes

- Port: 8080
- Database: postgres:16-alpine
- Create tables, forms, views, and APIs without code
- REST API auto-generated for every table
