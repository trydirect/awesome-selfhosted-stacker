# hn-briefing-agent — local deploy success

**Date:** 2026-10-20
**Stacker:** 0.3.4, Docker (macOS), target: local
**Template:** stacker.yml (built from pinned upstream commit, port 8000)

## Commands

```bash
cd stacker-projects/hn-briefing-agent
./scripts/generate-secrets.sh
stacker deploy --target local
```

## Verification

- `docker ps` → `hn-briefing-agent-app-1 Up (healthy)`
- `curl http://localhost:8000/docs` → HTTP 200 (FastAPI docs for the
  AgentScout Scheduler API)

## Notes

- FastAPI + uvicorn; the Gemini/ADK key and delivery settings (webhook or
  Gmail) are optional at start — needed for actual briefing runs.
- Teardown after verification: `stacker destroy -y`; project image removed
  afterwards (local image cleanup rule).
