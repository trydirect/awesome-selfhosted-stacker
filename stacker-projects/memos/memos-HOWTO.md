# Memos — Stacker Deploy HOWTO

Single container: `ghcr.io/usememos/memos:latest`. Lightweight note-taking with SQLite.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:5230/` in a browser.

Create an account on first visit.

## Notes

- Port: 5230
- Data: `memos_data` volume (SQLite database)
- Supports Markdown, tags, REST API
- No secrets needed
