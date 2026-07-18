# Ombi — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/ombi:latest`. Media request management for Plex/Jellyfin.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:3579/` in a browser.

## Notes

- Port: 3579
- Data: `ombi_config` volume
- Users can request movies and TV shows
- Integrates with Plex, Jellyfin, Radarr, Sonarr
