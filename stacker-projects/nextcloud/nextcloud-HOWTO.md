# Nextcloud — Stacker Deploy HOWTO

File sync and sharing. Three containers (nextcloud + mariadb + redis).

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
# The template generate-secrets.sh may miss DB_ROOT_PASSWORD and
# NEXTCLOUD_ADMIN_PASSWORD (sed-only without append fallback).
# Append them manually if missing:
echo "DB_ROOT_PASSWORD=$(openssl rand -hex 16)" >> .env
echo "NEXTCLOUD_ADMIN_PASSWORD=$(openssl rand -hex 16)" >> .env
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Verify

```bash
curl -I http://<SERVER_IP>:8080/
```

Expected: HTTP 302 or 400 (until trusted domain is configured).

## Notes

- Port: 8080
- mariadb on localhost:3306, redis on localhost:6379
- Set NEXTCLOUD_TRUSTED_DOMAINS in .env to your actual domain
