# langchain-chatchat — existing server deploy success

**Date:** 2026-10-16
**Stacker:** 0.3.4 (5cc1cac), target: existing server 167.233.196.133 (cpx42)
**Template:** stacker.yml (chatimage/chatchat:0.3.1.3-93e2c87-20240829 +
xprobe/xinference:v0.12.3-cpu)

## Commands

```bash
cd stacker-projects/langchain-chatchat
cp .env.example .env
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
export DEPLOY_HOST=167.233.196.133
stacker deploy --target server --server-host 167.233.196.133
```

Deploy history: #1376 (xinference GPU image crash-looped on CPU host),
#1377 after `xprobe/xinference:v0.12.3` → `v0.12.3-cpu` — **completed**.

## Verification

- `docker ps` → `project-app-1 Up (healthy)`, `project-xinference-1 Up (healthy)`
- `curl http://localhost:8501/_stcore/health` → `ok` (chatchat Streamlit health)
- `docker exec project-xinference-1 curl http://localhost:9997/status` →
  worker JSON with CPU/memory metrics (9997 is internal-only by design)
- service-to-service: `docker exec project-app-1 curl http://xinference:9997/status`
  → HTTP 200
- External: `curl http://167.233.196.133:8501/_stcore/health` → `ok` after
  `stacker cloud firewall add --public-ports 8501/tcp` (the cpx42's firewall
  is created with the first project's `public_ports` — 8501 had to be added)

## Notes

- RAM steady at ~1.6 GiB idle on cpx42; chatchat's Streamlit UI on 8501,
  xinference on internal 9997.
- The 2024-era images pull fine and run — the earlier "stale images" concern
  is disproven (see BUGS.md).
- Teardown between tests: server-side `docker compose -p project down --volumes`.
