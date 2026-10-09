# ai-knowledge-base — LOCAL deploy SUCCESS (with caveats)

**Date:** 2026-10-05
**Stacker:** v0.3.4 (2373565)
**Note:** `stacker.yml` declares `deploy.target: cloud`; local run forces `--target local`.

## Command

```bash
cd stacker-projects/ai-knowledge-base
stacker deploy --target local
```

## Verification

- `✓ Local deployment started successfully` (cosmetic `✗ Timeout waiting for containers`)
- 8/9 containers Up: app, web, worker, db (healthy), redis (healthy), qdrant, ollama, sandbox
- `curl http://127.0.0.1:3000/` → **307** (Dify web UI responding)
- `curl http://127.0.0.1:8080/` → 000 (see BUGS.md — port mapping wrong: dify-api listens on 5001, not 3000)

## Known Issues (see BUGS.md)

1. App port mapping `8080:3000` wrong — dify-api gunicorn binds 5001
2. NPM proxy crash-loops (letsencrypt volume missing in generated compose)
3. post_deploy hook fails locally (hardcoded `project-app-1` vs actual `ai-knowledge-base-app-1`)

## Cleanup

```bash
stacker destroy -y    # ✓ Stack destroyed successfully
```
