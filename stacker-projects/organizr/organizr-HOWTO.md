# Organizr — Stacker Deploy HOWTO

Single container: `organizr/organizr:latest`. HTPC/Homelab services organizer.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:9983/` in a browser.

## Notes

- Port: 9983
- Data: `organizr_config` volume
- Organize all your self-hosted apps in one dashboard
- User management with guest access
- Supports tabs, iframes, and API integrations
