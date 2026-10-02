# plausible — Local Deploy Success

**Date:** 2026-10-02
**Target:** local (`--target local` override)
**CLI:** stacker 0.3.4 (28a86cd)

Template uses `deploy.compose_file: docker/production/compose.yml` (checked-in
compose, not the generated `.stacker/docker-compose.yml` — that file is never
written for this project). Generator covers all required fields.

Notes:
- First start raced DNS (`nxdomain` for `plausible_db`) — container restarted
  itself and recovered (68 nxdomain lines then clean start).
- `../../.deploy-config/init-clickhouse.sql` bind source is missing in this repo
  (docker creates an empty dir) — ClickHouse still healthy, template artifact.

## Verification

| Check | Result |
|---|---|
| Containers | plausible, plausible_db (healthy), plausible_events_db (healthy) |
| HTTP `GET /` (8000) | 302 → `/register` **200** |
