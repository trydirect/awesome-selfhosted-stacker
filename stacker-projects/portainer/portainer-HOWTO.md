# Portainer — Stacker Deploy HOWTO

Single container: `portainer/portainer-ce:latest`. Docker container management web UI.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:9000/` in a browser.

Create an admin account on first visit.

## Notes

- Port: 9000
- Data: `portainer_data` volume
- Mounts Docker socket for container management
- Manage containers, images, volumes, networks via web UI
