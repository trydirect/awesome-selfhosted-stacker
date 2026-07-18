# changedetection.io — Stacker Deploy HOWTO

Single container: `ghcr.io/dgtlmoon/changedetection.io:latest`. Monitor websites for changes.

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

Add URLs to monitor. Get notified via email, Telegram, Slack, Discord, etc.

## Notes

- Port: 5000
- Data: `changedetection_data` volume
- Supports visual change detection, CSS selectors, JSON API monitoring
- No secrets needed
