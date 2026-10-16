# archon — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `ghcr.io/coleam00/archon:0.11.1`, port 3000)

## Commands

```bash
cd stacker-projects/archon
./scripts/generate-secrets.sh     # WEBHOOK_SECRET, TOKEN_ENCRYPTION_KEY, ...
stacker deploy --target local
```

## Verification

- `docker ps` → `archon-app-1 Up (healthy) 0.0.0.0:3000->3000/tcp`
- `curl http://localhost:3000/api/health` → `{"status":"ok",...
  "version":"0.11.1","is_docker":true,"activePlatforms":["Web"],...}`

## Notes

- Default storage is sqlite (`archon_data` / `archon_user_home` volumes);
  LLM keys (`CLAUDE_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN`) optional at start —
  needed at first run for actual AI usage.
- Teardown: `stacker destroy -y`; project image removed afterwards
  (`docker rmi ghcr.io/coleam00/archon:0.11.1`).
