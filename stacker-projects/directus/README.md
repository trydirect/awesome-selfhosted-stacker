# Directus

**Self-hosted headless CMS** — REST + GraphQL API for any database.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/directus

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Directus | 8055 | Headless CMS UI + API |
| PostgreSQL | 5432 | Database |
