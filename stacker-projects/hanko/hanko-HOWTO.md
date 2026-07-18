# Hanko — Stacker Deploy HOWTO

Two containers: `ghcr.io/teamhanko/hanko:latest` + `postgres:16-alpine`. Authentication platform with passkeys.

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

Open `http://<SERVER_IP>:8000/` in a browser.

## Notes

- Port: 8000
- Database: postgres:16-alpine
- Supports passkeys (WebAuthn), email OTP, social login
- Embeddable login widget for web apps
