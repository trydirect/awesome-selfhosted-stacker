# BookStack — Stacker Deploy HOWTO

Two containers: `lscr.io/linuxserver/bookstack:latest` + `lscr.io/linuxserver/mariadb:latest`. Documentation and wiki platform.

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

Open `http://<SERVER_IP>:6875/` in a browser.

Default login: `admin@example.com` / `password`

## Notes

- Port: 6875
- Database: MariaDB
- Supports Markdown, WYSIWYG, and code editor
- Organize content into Books → Chapters → Pages
