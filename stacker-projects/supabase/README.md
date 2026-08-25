# Supabase

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/supabase&ref=main)

**Self-hosted Firebase alternative** — Postgres, Auth, Realtime, Storage, Edge Functions.

## One-click deploy on TryDirect

Click the badge above, or open the deep link:

```markdown
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/supabase&ref=main
```

## Manual deploy

### Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/supabase

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Kong (API Gateway) | 8000 | REST API proxy |
| Studio | 3000 | Dashboard UI |
| PostgREST | 3000 | Auto-generated REST API |
| GoTrue | 9999 | Authentication |
| Realtime | 4000 | Realtime subscriptions |
| Storage | 5000 | File storage |
| Edge Functions | 9000 | Serverless functions |
