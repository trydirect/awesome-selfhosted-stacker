# Calibre-web — Stacker Deploy HOWTO

Single container: `linuxserver/calibre-web:latest`. E-book management with web reader.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8083/` in a browser.

Default login: `admin` / `admin123`

Set the Calibre library location to `/books` on first login.

## Notes

- Port: 8083
- Config: `calibre_config` volume
- Library: `calibre_library` volume (upload EPUBs/PDFs here)
- Supports OPDS feed for e-reader apps
