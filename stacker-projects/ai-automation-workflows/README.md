# AI Automation Workflows

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/ai-automation-workflows&ref=main)

**Self-hosted AI workflow automation** — Flowise + n8n + Ollama + Qdrant.

## One-click deploy on TryDirect

Click the badge above, or open the deep link:

```markdown
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/ai-automation-workflows&ref=main
```

TryDirect validates the stack's `stacker.yml`, presents the `.env.example` fields
(secrets generated for you — the repo's `generate-secrets.sh` is never executed),
and clones a pre-baked Hetzner snapshot. No SSH key, no account-API credentials
needed.

## Manual deploy

### Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/ai-automation-workflows

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy to your server
stacker deploy
```

### Manual Docker Compose deploy

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/ai-automation-workflows

cp .stacker/docker-compose.yml .
docker compose up -d --build
```

> Note: stack `name`/`project.identity` are kept as `ai-workflows-v2` for prod
> continuity (see `stacker.yml`) — the folder is the human-readable slug.