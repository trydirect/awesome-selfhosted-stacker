# Syncthing

**Self-hosted file synchronization** — continuous file synchronization between devices.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/syncthing

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Syncthing | 8384 | File sync UI |
