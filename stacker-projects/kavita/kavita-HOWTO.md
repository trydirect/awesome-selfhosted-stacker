# Kavita — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/kavita:latest`. Self-hosted reading server for books, manga, and comics.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:5000/` in a browser.

Create an admin account on first visit.

## Notes

- Port: 5000
- Config: `kavita_config` volume
- Library: `kavita_library` volume (upload EPUBs, CBZ, CBR, PDF)
- OPDS support for e-reader apps
- Built-in book reader with progress sync
