# Ghost — Stacker Deploy HOWTO

Blogging platform. Two containers (ghost app + mysql).

## Setup

```bash
cp .env.example .env && ./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Verify

```bash
curl -I http://<SERVER_IP>:2368/
```
Expected: HTTP 200

## Notes

- Port: 2368
- mysql on localhost:3306 (not exposed externally)
- mysql data in named volume `mysql_data`
- Ghost content in named volume `ghost_content`
