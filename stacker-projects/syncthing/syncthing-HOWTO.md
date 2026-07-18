# Syncthing — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/syncthing:latest`. P2P file synchronization.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8384/` in a browser.

## Notes

- Port: 8384 (web UI), 22000 (sync protocol)
- Data: `syncthing_config` (settings), `syncthing_data` (synced files)
- Decentralized Dropbox alternative
- No cloud dependency — files stay on your devices
