# One Time Secret — Stacker Deploy HOWTO

Two containers: `onetimesecret/onetimesecret:latest` + `redis:7-alpine`. Share secrets with self-destructing links.

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

Open `http://<SERVER_IP>:3000/` in a browser.

Paste a secret, set a passphrase and expiration, share the link.

## Notes

- Port: 3000
- Redis: `onetimesecret-redis` service
- Secrets self-destruct after viewing
