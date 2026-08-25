# Mealie

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/mealie&ref=main)

**Self-hosted recipe manager** — organize, search, and share your recipes.

## One-click deploy on TryDirect

Click the badge above, or open the deep link:

```markdown
https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/mealie&ref=main
```

## Manual deploy

### Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/mealie

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Mealie | 9925 | Recipe manager UI |
