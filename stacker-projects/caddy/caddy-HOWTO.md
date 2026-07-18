# Caddy — Stacker Deploy HOWTO

Single container: `caddy:latest`. Web server with automatic HTTPS.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>/` in a browser.

## Notes

- Port: 80 (HTTP), 443 (HTTPS)
- Data: `caddy_data` (certificates), `caddy_config` (config)
- Automatic Let's Encrypt certificates
- Reverse proxy, static file server, API gateway
- Configure via Caddyfile in the container
