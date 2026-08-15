# AI Knowledge Base

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/ai-knowledge-base&ref=main)

**Self-hosted AI knowledge base** — Dify + PostgreSQL + Redis + Weaviate + Sandbox.

## One-click deploy on TryDirect

Click the badge above, or open the deep link:

```markdown
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/ai-knowledge-base&ref=main
```

TryDirect validates the stack's `stacker.yml`, presents the `.env.example` fields
(secrets generated for you — the repo's `generate-secrets.sh` is never executed),
and clones a pre-baked Hetzner snapshot. No SSH key, no account-API credentials
needed.

## Manual deploy

### Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/ai-knowledge-base

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

### Deploy with Docker Compose

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/ai-knowledge-base

# Copy compose file and build
cp .stacker/docker-compose.yml .
docker compose up -d --build
```
