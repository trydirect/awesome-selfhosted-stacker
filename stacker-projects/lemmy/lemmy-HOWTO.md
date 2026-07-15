# Lemmy — Stacker Deploy HOWTO

Three containers: app (dessalines/lemmy:0.19.11) + postgres:16-alpine + asonix/pictrs.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Post-deploy: create Lemmy config

Lemmy requires a `lemmy.hjson` config file. After deploy, create it on the server:

```bash
ssh root@<SERVER_IP> "cat > /home/trydirect/project/lemmy.hjson << 'EOF'
{
  database: {
    host: \"project-lemmy_db-1\"
    port: 5432
    user: \"lemmy\"
    password: \"<DB_PASSWORD from .env>\"
    database: \"lemmy\"
  }
  hostname: \"<SERVER_IP>\"
  jwt_secret: \"<JWT_SECRET from .env>\"
  admin: {
    username: \"admin\"
    password: \"<ADMIN_PASSWORD from .env>\"
  }
}
EOF"
```

Then restart the app: `docker restart project-app-1`

## Verify

```bash
curl -I http://<SERVER_IP>:8536/
```

## Notes

- Port: 8536
- postgres on localhost:5432, pictrs on localhost:6969
- `dessalines/lemmy:latest` doesn't exist — use a specific version tag
- Named volumes: lemmy_db, lemmy_pictrs
