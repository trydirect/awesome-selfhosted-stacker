# Floci — Stacker Deploy HOWTO

Single container: floci/floci:latest. Local AWS service emulator (S3, Lambda, RDS, etc.).

## Setup

```bash
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Verify

```bash
curl -I http://<SERVER_IP>:4566/
```

## Notes

- Port: 4566
- Mounts docker.sock for Docker-in-Docker operations
- Data directory (`./data`) is auto-created on the target host
- TLS enabled by default — use HTTPS for SDK connections
