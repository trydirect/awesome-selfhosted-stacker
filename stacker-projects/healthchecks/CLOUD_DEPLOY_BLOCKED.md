# healthchecks — Cloud Deploy: BLOCKED (environment, not project config)

**Target:** cloud (Hetzner, fresh server via `htz-0`)
**Date:** 2026-08-22
**Status:** Not completed — blocked by an environment/infra issue that
could not be diagnosed from the stacker CLI.

## What was verified

- `proxy: traefik` config parsed and applied correctly — `stacker status`
  showed:
  ```
  ── Proxy ── Type: traefik
  ── App URLs ── https://healthchecks.example.com → app:8000
  ```
- Secrets managed via `stacker secrets set KEY=VALUE` (local `.env` mode):
  `DB_PASSWORD`, `SECRET_KEY` set and masked in `stacker secrets list`,
  `stacker secrets validate` confirmed all `${VAR}` references resolved.

## What blocked it

Three consecutive `--force-new` deploys (servers 558, 559, 560) all
paused with the generic `local-exec provisioner error`, and all three
were assigned the **same recycled IP 49.12.47.82**, which is
SSH-unreachable from the test machine (`ssh`/`ping` both time out — no
firewall was created either: `stacker cloud firewall list --server-id
558` → "No firewall attached").

The real cause could **not** be determined from the stacker CLI —
`stacker deployment events` only ever returned the generic
`local-exec provisioner error` with no underlying task stderr (this is
exactly the observability gap filed as
[stacker#241](https://github.com/trydirect/stacker/issues/241)).

Working (unconfirmed) theory: `monitoring.status_panel: true` binds port
5000, and each paused retry on the recycled IP may have left a
statuspanel container occupying 5000, so subsequent retries collide — the
same class as the `Bind for 0.0.0.0:5000 failed: port is already
allocated` failure documented in #241. Could not confirm because the host
is unreachable.

Per user direction, skipped rather than burning further servers.

## Not a project/config bug

The `stacker.yml` (traefik proxy, secrets, services) is correct at the
parse/plan level. Blockage is infra/observability, tracked in #241.
See `BUGS.md` for the local port-8000 conflict (also environment, not a
bug).
