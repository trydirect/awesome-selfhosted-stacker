# Keycloak — Stacker Deploy HOWTO

Two containers: `quay.io/keycloak/keycloak:latest` + `postgres:16-alpine`. Identity and access management (SSO).

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

Login with `admin` / password from `.env`.

## Notes

- Port: 8080
- Database: postgres:16-alpine
- Supports OAuth2, OIDC, SAML, LDAP
- Centralized SSO for all your self-hosted apps
- Running in dev mode (`start-dev`) — use `start` for production
