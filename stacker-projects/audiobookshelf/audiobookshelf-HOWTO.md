# Audiobookshelf — Stacker Deploy HOWTO

Single container: `ghcr.io/advplyr/audiobookshelf:latest`. Audiobook and podcast server.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:13378/` in a browser.

Create an admin account on first visit.

## Add audiobooks

Upload audiobook files to the `audiobooks_data` volume.

## Notes

- Port: 13378
- Data: `audiobooks_data` (media), `audiobooks_config` (settings), `audiobooks_metadata` (covers, metadata)
- Supports M4B, MP3, M4A, FLAC, OPUS, OGG
- Android/iOS apps available
