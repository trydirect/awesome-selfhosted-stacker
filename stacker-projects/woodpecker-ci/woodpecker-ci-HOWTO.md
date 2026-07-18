# Woodpecker CI — Stacker Deploy HOWTO

Two containers: `woodpeckerci/woodpecker-server:latest` + `woodpeckerci/woodpecker-agent:latest`. CI/CD pipeline engine.

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

- Port: 8000 (server)
- Agent connects to server via Docker socket
- Supports GitHub, GitLab, Gitea as forge backends
- Configure forge integration via environment variables
