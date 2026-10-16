# speaches — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `ghcr.io/speaches-ai/speaches:0.8.3-cpu`, port 8000)

## Commands

```bash
cd stacker-projects/speaches
./scripts/generate-secrets.sh     # .env from .env.example, API_KEY=openssl rand -hex 16
stacker deploy --target local
```

## Verification

- `docker ps` → `speaches-app-1 Up (healthy) 0.0.0.0:8000->8000/tcp`
- `curl -H "Authorization: Bearer $API_KEY" http://localhost:8000/health` → `OK`
  (template healthcheck passes; container reports healthy)

## Notes

- CLI printed `✗ Timeout waiting for containers` even though the container was
  healthy within ~30s — CLI wait false-negative, deploy itself succeeded.
- Teardown: `stacker destroy -y`; project image removed afterwards
  (`docker rmi ghcr.io/speaches-ai/speaches:0.8.3-cpu`).
