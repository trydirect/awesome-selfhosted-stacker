# Stirling PDF

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/stirling-pdf&ref=main)

**Self-hosted PDF manipulator** — merge, split, convert, OCR, and more.

## One-click deploy on TryDirect

Click the badge above, or open the deep link:

```markdown
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/stirling-pdf&ref=main
```

TryDirect validates the stack's `stacker.yml`, presents the `.env.example` fields
(secrets generated for you — the repo's `generate-secrets.sh` is never executed),
and clones a pre-baked Hetzner snapshot. No SSH key, no account-API credentials
needed.

## Manual deploy

### Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/stirling-pdf

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

### Deploy with Docker Compose

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/stirling-pdf

# Copy compose file and build
cp .stacker/docker-compose.yml .
docker compose up -d --build
```
