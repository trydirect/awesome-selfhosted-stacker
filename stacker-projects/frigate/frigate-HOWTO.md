# Frigate — Stacker Deploy HOWTO

Single container: `ghcr.io/blakeblackshear/frigate:stable`. NVR with real-time AI object detection.

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

Open `http://<SERVER_IP>:5000/` in a browser.

## Notes

- Port: 5000 (web UI), 8554 (RTSP), 8555 (WebRTC)
- Runs privileged for USB device access (Coral TPU)
- Configure cameras in `config.yml` inside the container
- AI object detection with CPU or Coral TPU
- Integrates with Home Assistant
