# FreshRSS — Stacker Deploy HOWTO

Single container: `lscr.io/linuxserver/freshrss:latest`. Self-hosted RSS reader.

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Access

Open `http://<SERVER_IP>:8080/` in a browser.

Complete the installation wizard on first visit.

## Notes

- Port: 8080
- Data: `freshrss_data` volume
- Supports Fever API, Google Reader API for mobile clients
- Mobile apps: Reeder, FeedMe, NewsFlash
