# Mealie — Stacker Deploy HOWTO

Single container: `ghcr.io/mealie-recipes/mealie:latest`. Recipe manager with import, meal planning, and shopping lists.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:9925/` in a browser.

Default credentials: `changeme@example.com` / `MyPassword`

## Notes

- Port: 9925 (maps to container port 9000)
- Data: `mealie_data` volume
- Supports recipe import from URLs, meal planning, shopping lists
- No external database needed (SQLite)
