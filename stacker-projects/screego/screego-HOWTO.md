# Screego — Stacker Deploy HOWTO

Single container: `ghcr.io/screego/server:latest`. Screen sharing via WebRTC.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:5050/` in a browser.

Click "Create Room" and share the URL.

## Notes

- Port: 5050 (Web UI)
- TURN ports: 10000:10100/udp (WebRTC media)
- No secrets needed
- Set `SCREEGO_EXTERNAL_IP=<SERVER_IP>` if auto-detection fails
