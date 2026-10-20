# excaliflow — local deploy success

**Date:** 2026-10-20
**Stacker:** 0.3.4, Docker (macOS), target: local
**Template:** stacker.yml (built from pinned upstream commit, port 3000)

## Commands

```bash
cd stacker-projects/excaliflow
./scripts/generate-secrets.sh
stacker deploy --target local
```

## Verification

- `docker ps` → `excaliflow-app-1 Up (healthy)`
- `curl http://localhost:3000/` → HTTP 200 (diagram editor UI)

## Notes

- Plain Node static server (no build step); image builds by fetching the
  pinned upstream commit.
- Teardown after verification: `stacker destroy -y`; project image removed
  afterwards (local image cleanup rule).
