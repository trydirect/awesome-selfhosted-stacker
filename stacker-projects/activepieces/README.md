# Activepieces

**Self-hosted workflow automation** — Zapier/Make alternative with visual workflow builder.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/activepieces

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Activepieces | 8080 | Workflow automation UI |
| PostgreSQL | 5432 | Database |
