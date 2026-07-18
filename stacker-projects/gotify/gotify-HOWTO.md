# Gotify — Stacker Deploy HOWTO

Single container: `gotify/server:latest`. Push notification server.

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

Open `http://<SERVER_IP>:8080/` in a browser.

Login with admin credentials from `.env`.

## Send notifications

```bash
# Create an app token in the web UI first
curl "http://<SERVER_IP>:8080/message?token=YOUR_APP_TOKEN" \
  -F "title=Hello" -F "message=World" -F "priority=5"
```

## Notes

- Port: 8080
- Data: `gotify_data` volume
- Android app: Gotify on F-Droid / Google Play
