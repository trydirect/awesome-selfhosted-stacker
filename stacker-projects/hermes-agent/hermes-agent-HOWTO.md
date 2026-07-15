# Hermes Agent — Stacker Deploy HOWTO

AI agent runtime. Single container (built from Dockerfile).

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
curl -I http://<SERVER_IP>:8000/
curl -I http://<SERVER_IP>:8001/
```

## Notes

- Ports: 8000, 8001
- No external dependencies or services
- Builds from local Dockerfile (type: python with dockerfile: Dockerfile)
- Minimal .env (HERMES_UID, HERMES_GID)
