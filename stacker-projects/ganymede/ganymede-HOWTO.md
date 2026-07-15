# Ganymede — Stacker Deploy HOWTO

Twitch VOD archiving tool. Two containers (app + postgres).

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
# Set TWITCH_CLIENT_ID and TWITCH_CLIENT_SECRET in .env for Twitch API access
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Verify

```bash
curl -I http://<SERVER_IP>:4800/
```
Expected: HTTP 200

## Notes

- Port: 4800
- postgres on localhost:5432
- Named volumes: ganymede_videos, ganymede_temp, ganymede_logs, ganymede_config, ganymede_postgres_data
- Twitch API credentials required for full functionality
