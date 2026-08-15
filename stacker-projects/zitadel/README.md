# Zitadel

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/zitadel&ref=main)

**Self-hosted identity management** — Auth0/Keycloak alternative with OIDC, SAML, MFA.

## One-click deploy on TryDirect

Click the badge above, or open the deep link:

```markdown
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/zitadel&ref=main
```

## Manual deploy

### Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/zitadel

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Zitadel | 8080 | Identity management console |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Cache |
