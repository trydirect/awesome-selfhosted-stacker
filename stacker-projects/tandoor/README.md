# Tandoor

**Self-hosted recipe manager** — organize and share your recipes.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/tandoor

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Tandoor | 8080 | Recipe manager UI |
| PostgreSQL | 5432 | Database |
