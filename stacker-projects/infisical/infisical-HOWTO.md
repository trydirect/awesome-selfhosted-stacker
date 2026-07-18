# Infisical — Stacker Deploy HOWTO

Two containers: `infisical/infisical:v0.162.9` + `postgres:16-alpine`. Secret management platform.

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

Create an account on first visit.

## Notes

- Port: 8080
- Database: postgres:16-alpine
- Supports secret versioning, RBAC, audit logs
- SDKs: Node, Python, Go, Ruby, Java, .NET
