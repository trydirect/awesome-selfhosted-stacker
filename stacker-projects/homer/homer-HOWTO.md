# Homer — Stacker Deploy HOWTO

Single container: `b4bz/homer:latest`. No database needed. Static dashboard for your self-hosted apps.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

Edit `config.yml` to add your own services.

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8080/` in a browser.

## Customize

Edit `config.yml` before deploying. The file is bind-mounted into the container.

## Notes

- Port: 8080
- Config: `config.yml` → `/www/assets/config.yml` (bind-mounted)
- Named volume: `homer_config` (for static assets)
