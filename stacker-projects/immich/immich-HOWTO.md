# Immich — Stacker Deploy HOWTO

Three containers: `ghcr.io/immich-app/immich-server:latest` + `tensorchord/pgvecto-rs:pg16` + `redis:7-alpine`. Self-hosted photo/video management (Google Photos alternative).

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

Open `http://<SERVER_IP>:2283/` in a browser.

Create an account on first visit.

## Notes

- Port: 2283
- Database: pgvecto-rs (PostgreSQL with vector extension for ML features)
- Redis for caching
- Mobile apps: iOS and Android
- Supports face recognition, search by location, timeline
