# Navidrome — Stacker Deploy HOWTO

Single container: `deluan/navidrome:latest`. Music streaming server.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:4533/` in a browser.

Create an admin account on first visit.

## Add music

Upload music files to the `navidrome_music` volume. Navidrome scans hourly by default.

## Notes

- Port: 4533
- Data: `navidrome_data` volume (database, covers)
- Music: `navidrome_music` volume (bind-mount your music folder or upload to the volume)
- Supports Subsonic API clients (DSub, Ultrasonic, etc.)
