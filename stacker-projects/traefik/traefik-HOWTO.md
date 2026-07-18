# Traefik — Stacker Deploy HOWTO

Single container: `traefik:v3.0`. Cloud-native reverse proxy with auto-discovery.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

- Dashboard: `http://<SERVER_IP>:8080/`
- HTTP: `http://<SERVER_IP>:80/`
- HTTPS: `https://<SERVER_IP>:443/`

## Notes

- Port: 80 (HTTP), 443 (HTTPS), 8080 (dashboard)
- Mounts Docker socket for auto-discovery
- Auto-detects containers with Traefik labels
- Automatic Let's Encrypt certificates
