# Romm — Stacker Deploy HOWTO

Two containers: app (rommapp/romm:latest) + mariadb:11.

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Troubleshooting

### Stale MariaDB volume

If the server has leftover data from a previous MariaDB deployment, remove it:

```bash
ssh root@<SERVER_IP> "docker volume rm -f project_mysql_data"
stacker deploy --target server
```

## Verify

```bash
curl -I http://<SERVER_IP>:8080/
```

## Notes

- Port: 8080
- mariadb on localhost:3306
- Named volumes: mysql_data, romm_resources, romm_redis_data
- Directory bind mounts (./library, ./assets, ./config) are auto-created on the target host
