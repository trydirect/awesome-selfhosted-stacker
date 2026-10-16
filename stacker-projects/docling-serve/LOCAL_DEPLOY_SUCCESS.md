# docling-serve — local deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), Docker 29.8.2, macOS (arm64 host)
**Template:** stacker.yml (image `ghcr.io/docling-project/docling-serve-cpu:v1.37.0`, port 5001)

## Commands

```bash
cd stacker-projects/docling-serve
./scripts/generate-secrets.sh     # .env from .env.example, DOCLING_SERVE_API_KEY
stacker deploy --target local
```

## Verification

- `docker ps` → `docling-serve-app-1 Up (healthy) 0.0.0.0:5001->5001/tcp`
- `curl http://localhost:5001/health` → `{"status":"ok"}` (also with `X-Api-Key` header)
- UI enabled via `DOCLING_SERVE_ENABLE_UI=1`

## Notes

- First boot needs up to 120s (healthcheck `start_period`); container became
  healthy on first pass.
- CLI printed the known `✗ Timeout waiting for containers` false-negative
  (root BUGS.md:1063).
- Teardown: `stacker destroy -y`; project image removed afterwards
  (`docker rmi ghcr.io/docling-project/docling-serve-cpu:v1.37.0`).
