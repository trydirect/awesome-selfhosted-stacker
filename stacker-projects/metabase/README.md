# Metabase

**Self-hosted business intelligence** — easy-to-use analytics and dashboarding.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/metabase

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Metabase | 3000 | BI dashboard UI |
| PostgreSQL | 5432 | Database |
