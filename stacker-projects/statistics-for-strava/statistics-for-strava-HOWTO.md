# Statistics for Strava — Stacker Deploy HOWTO

Two containers: app + daemon (both robiningelbrecht/strava-statistics:latest).

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
# Fill in Strava API credentials:
#   STRAVA_CLIENT_ID, STRAVA_CLIENT_SECRET, STRAVA_REFRESH_TOKEN
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Post-deploy

The app needs a config.yaml to start. Mount the strava_database volume and create it,
or check logs for the expected config path:

```bash
ssh root@<SERVER_IP> "docker logs project-app-1 --tail 20"
```

## Verify

```bash
curl -I http://<SERVER_IP>:8081/
```

## Notes

- Port: 8081
- Named volumes: strava_database, strava_files, strava_gear_maintenance, strava_watch
- Both app and daemon share the same image with different commands
