# bunkerweb — Existing Server Deploy Success

**Date:** 2026-10-30
**Stacker:** 0.3.4 (6123cee), target: existing server 78.47.139.250 (Hetzner
cpx22 `bunkerweb-202d`, id=943 — this project's own spare cloud server from
deployment #1520, per the fresh-per-project-server direction; the forbidden
shared host 46.224.127.228 in `.env` was explicitly overridden)
**Template:** stacker.yml (fixed: `bunkerity/bunkerweb-all-in-one:1.6.17` +
redis:7.4-alpine — see CLOUD_DEPLOY_SUCCESS.md for the fix)
**Deployment:** #1523 (hash `deployment_f03b0d13-35e9-4c0e-ae04-20fb06694126`)

## Commands

```bash
cd stacker-projects/bunkerweb
./scripts/generate-secrets.sh
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples
export DEPLOY_HOST=78.47.139.250            # overrides .env's shared-host value
stacker deploy --target server --server-host 78.47.139.250
```

`--server-host` sets `deploy.server.host` without editing `stacker.yml`
(template stays canonical); `export DEPLOY_HOST=...` is belt-and-braces
against `${DEPLOY_HOST}` resolving to the forbidden shared host.

## Verification

| Check | Result |
|---|---|
| `stacker status` | ✓ Deployment #1523 — completed |
| `stacker agent status --deployment <hash>` (pinned per stacker#234) | ● online; `project-app-1` (all-in-one) + `project-redis-1` running |
| `curl http://78.47.139.250/` | 301 → https |
| `curl -L http://78.47.139.250/` | **200** at `https://78.47.139.250/setup` |
| `curl https://78.47.139.250/` | 302 → `/setup` |
| `curl http://78.47.139.250:7000/` | 303 → `/setup` (web UI direct) |

Same first-run state as the cloud target: the BunkerWeb **setup wizard** at
`/setup` (200) until an admin account and `SERVER_NAME` are configured.

Notes:
- The `--target server` flow emitted **no `✓ Your SSH key authorized` line**
  (that marker is part of cloud provisioning) — per repo rules SSH-based
  checks are therefore inconclusive and were not used as evidence; all
  verification is via `stacker` CLI + external HTTP.
- stacker#240 context: `--target server` writes to the shared remote path
  (`/home/trydirect/project`) — deploying bunkerweb onto bunkerweb's own
  dedicated server makes the overwrite same-project-only (the reason the
  shared host 46.224.127.228 was not used).
- Server left running (servers are never deleted).
