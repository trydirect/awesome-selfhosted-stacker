# daily-stars-explorer — Stacker Deploy HOWTO

Shows daily GitHub stars for repos. Single-container, no external DB.

## Prerequisites

- Stacker v0.3.0+ installed and authenticated
- SSH key ready for server access
- (Optional) A GitHub PAT in `.env.PAT` to avoid API rate limits

## Setup

```bash
# Populate .env
cp .env.example .env
# Edit .env and set PAT if needed

# Configure target server
stacker config setup server \
  --ip <SERVER_IP> \
  --user root \
  --key ~/.ssh/id_ed25519
```

## Deploy

```bash
stacker deploy --target server --force-rebuild
```

## Verify

```bash
curl -I http://<SERVER_IP>:8080/
```

Expected: HTTP 200

## Notes

- Bind mounts: none
- pre_build hook: no-op (no secrets to generate)
