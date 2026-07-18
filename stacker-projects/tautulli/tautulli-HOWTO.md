# Tautulli — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/tautulli:latest`. Plex Media Server monitoring and analytics.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8181/` in a browser.

## Notes

- Port: 8181
- Data: `tautulli_config` volume
- Monitor Plex watch history, streaming stats, library stats
- Notifications for new content, playback events
