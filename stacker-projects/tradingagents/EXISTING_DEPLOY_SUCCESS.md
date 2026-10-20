# tradingagents — existing server deploy success

**Date:** 2026-10-20
**Stacker:** 0.3.4, target: existing server 5.75.239.54 (Hetzner cpx42)
**Template:** stacker.yml (image `optimum/tradingagents:1.0.0`, built from the
pinned upstream commit in the template Dockerfile)

## Commands

```bash
cd stacker-projects/tradingagents
./scripts/generate-secrets.sh        # .env from .env.example (LLM keys user-supplied)
export BASE_PATH=... DEPLOY_HOST=5.75.239.54
export STACKER_DOCKER_USERNAME=... STACKER_DOCKER_PASSWORD=...   # registry pull
stacker deploy --target server --server-host 5.75.239.54
```

## Verification

- `docker ps` → `project-app-1 Up (healthy)`
- `docker exec project-app-1 tradingagents --help` → full CLI usage
  (TradingAgents CLI: Multi-Agents LLM Financial Trading Framework)

## Notes

- **The app is a one-shot CLI** (analysis runs and exits; no web UI, no
  daemon). The image therefore keeps the container alive
  (`CMD ["sleep", "infinity"]`) so analyses run via:
  `docker exec -it <container> tradingagents --ticker NVDA --date 2026-10-20 ...`
- Image is published at Docker Hub (currently private); the template's
  `deploy.registry` carries `${STACKER_DOCKER_USERNAME}`/`${STACKER_DOCKER_PASSWORD}`
  references resolved at deploy time. For marketplace publishing the image
  should be public — Hub API refused the visibility change, do it in the Hub UI.
- Remote deploys require a pre-built `app.image` (dockerfile builds are
  local-only); the template Dockerfile is the source of that image.
- Deploy history: #1393 (interactive entrypoint restart-looped),
  #1394 (server kept the cached old image under the same tag), #1395 after
  `docker rmi` on the server — completed and healthy.
