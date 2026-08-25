# Nextcloud

**Self-hosted content collaboration platform** — file sync, share, and productivity tools.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/nextcloud

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Nextcloud | 8081 | Content collaboration UI |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
