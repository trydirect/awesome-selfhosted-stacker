# rag-as-a-service — local deploy success

**Date:** 2026-10-20
**Stacker:** 0.3.4, Docker (macOS), target: local
**Template:** stacker.yml (built from pinned upstream commit, port 8501)

## Commands

```bash
cd stacker-projects/rag-as-a-service
./scripts/generate-secrets.sh
stacker deploy --target local
```

## Verification

- `docker ps` → `rag-as-a-service-app-1 Up (healthy)`
- `curl http://localhost:8501/` → HTTP 200 (Streamlit UI)

## Notes

- Streamlit RAG demo; API keys (Ragie, Anthropic) are entered in the app UI,
  nothing to configure in .env.
- Teardown after verification: `stacker destroy -y`; project image removed
  afterwards (local image cleanup rule).
