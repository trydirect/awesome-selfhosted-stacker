# Supabase + PostHog

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/supabase-posthog&ref=main)

**Self-hosted Supabase + PostHog analytics** — Postgres, Auth, Realtime, Storage + Product Analytics.

## One-click deploy on TryDirect

Click the badge above, or open the deep link:

```markdown
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/supabase-posthog&ref=main
```

## Manual deploy

### Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/supabase-posthog

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
| PostHog | 8001 | Product analytics |
| Studio | 3000 | Dashboard UI |
| PostgREST | 3000 | Auto-generated REST API |
| GoTrue | 9999 | Authentication |
| Realtime | 4000 | Realtime subscriptions |
| Storage | 5000 | File storage |
