# Vaultwarden

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/vaultwardenquick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/vaultwarden&ref=mainref=e68926c)

**Self-hosted password manager** — Bitwarden-compatible server written in Rust.

## One-click deploy on TryDirect

Click the badge above, or open the deep link:

```markdown
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/vaultwardenquick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/vaultwarden&ref=mainref=e68926c
```

## Manual deploy

### Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/vaultwarden

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Vaultwarden | 8080 | Password manager UI |
