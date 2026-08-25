# n8n

**Self-hosted workflow automation** — Zapier alternative with visual workflow editor.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/n8n

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| n8n | 5678 | Workflow automation UI |
| PostgreSQL | 5432 | Database |
