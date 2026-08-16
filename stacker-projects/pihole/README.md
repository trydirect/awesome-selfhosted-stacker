# Pi-hole

**Self-hosted DNS ad-blocker** — network-wide ad blocking.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/pihole

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Pi-hole | 8080 | DNS ad-blocker UI |
