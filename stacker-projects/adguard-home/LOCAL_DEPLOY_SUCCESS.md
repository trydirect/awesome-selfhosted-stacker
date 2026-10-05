# adguard-home — LOCAL deploy SUCCESS

**Date:** 2026-10-04
**Stacker:** v0.3.4 (2373565)
**Note:** `stacker.yml` declares `deploy.target: server`; local run forces `--target local`.

## Command

```bash
cd stacker-projects/adguard-home
stacker deploy --target local
```

## Verification

- `✓ Local deployment started successfully` (deploy also printed the usual
  cosmetic `✗ Timeout waiting for containers` — AdGuard has no healthcheck;
  container was Up and serving before the timeout expired)
- `docker ps`: `adguard-home-app-1 Up`, mappings
  `0.0.0.0:3000->3000/tcp`, `0.0.0.0:8080->80/tcp`, `0.0.0.0:8053->53/tcp+udp`
- `curl http://127.0.0.1:3000/` → **302** (redirect to setup wizard —
  expected for a fresh AdGuard Home; logs: `webapi: AdGuard Home is available...
  starting plain server addr=0.0.0.0:3000`)
- Ports 8080 (HTTP) and 8053 (DNS) answer only after the first-run setup
  wizard completes — fresh-instance behavior, not a template defect.

## Cleanup

```bash
stacker destroy -y    # ✓ Stack destroyed successfully, container gone
```
Named volumes `adguard-home_adguard_conf` / `adguard-home_adguard_work`
intentionally kept (no `--volumes`). Destroy resolved the correct compose
project (`-p adguard-home`) — its `.env` defines `DEPLOY_HOST`/`BASE_PATH`,
so `StackerConfig::from_file` succeeds (contrast: AstrBot, root BUGS.md
false-success entry).
