# Paperless-ngx

**Self-hosted document management** — scan, index, and archive your documents.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/paperless-ngx

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Paperless-ngx | 8000 | Document management UI |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
