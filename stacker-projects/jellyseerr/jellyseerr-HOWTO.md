# Jellyseerr — Stacker Deploy HOWTO

Single container: `fallenbagel/jellyseerr:latest`. Media request management for Jellyfin/Plex.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:5055/` in a browser.

Configure Jellyfin/Plex connection on first visit.

## Notes

- Port: 5055
- Data: `jellyseerr_config` volume
- Integrates with Jellyfin, Plex, Radarr, Sonarr
- Users can request movies and TV shows
