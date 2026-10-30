# bunkerweb — known issues

## [BLOCKED] Local deploy: port 7000 conflict with macOS AirPlay Receiver

**Date:** 2026-10-30
**CLI:** stacker 0.3.4 (6123cee)

Steps to reproduce:
1. `cd stacker-projects/bunkerweb`
2. `stacker deploy --target local`

Expected behaviour:
Container ports 80/443/7000 bind on the host (stacker.yml `app.ports`).

Actual behaviour:
Stacker refused before deploying — its port-conflict validation fired:

```
  Hook (pre_build) running: /Users/vasilipascal/work/stacker-project-examples/stacker-projects/bunkerweb/scripts/generate-secrets.sh
Secrets ready. (No secrets needed for BunkerWeb)

  Hook (pre_build) completed
  ✗ Deployment to local failed: Host port conflict detected before deploy:
  • port 7000 (service 'app') is already allocated on this host — find the owner with: lsof -nP -iTCP:7000 -sTCP:LISTEN
```

Logs / Evidence:
- `lsof -nP -iTCP:7000 -sTCP:LISTEN` → `ControlCe 805 ... TCP *:7000 (LISTEN)`
  (macOS AirPlay Receiver binds *:7000 on this test host).
- Ports 80, 443, 6379 and the pre-build hook are fine; the refusal is only
  the 7000 mapping (`7000:7000/tcp`, BunkerWeb web UI / API).

This is stacker's port-conflict validation working correctly, not a CLI bug —
same pattern as the `[BLOCKED]` entry in `../healthchecks/BUGS.md` (port 8000).
Freeing 7000 requires disabling the host's AirPlay Receiver (system settings
change) or editing the fixture's `stacker.yml` port mapping — neither done
without explicit approval. Skipped local deploy; cloud/existing-server phases
cover the stack where 80/443/7000 are free.

## [BUG] config_contract exposes `POSTGRES_DB` on the `redis` service

**Date:** 2026-10-30

Steps to reproduce:
1. Read `stacker.yml` → `config_contract.services.redis.fields` (or the
   marketplace long_description "What you configure" section).

Expected behaviour:
Only fields that exist for the service. `redis` (redis:7.4-alpine) has no
`POSTGRES_DB` variable anywhere in the stack.

Actual behaviour:
`POSTGRES_DB` is listed as an editable field on the `redis` service, and the
marketplace `long_description` advertises it ("`API_HOST`, `API_PORT`,
`REDIS_HOST`, `REDIS_PORT`, `POSTGRES_DB` ship prefilled"). Looks like a
copy-paste artifact from a postgres-based template; buyers would see a
meaningless knob in the deploy form.

Logs / Evidence:
`stacker.yml` lines under `config_contract.services.redis.fields` and the
`marketplace.long_description` "What you configure" bullet list.

## [BUG] Stale deployment state: `stacker status` reports "completed" for a deleted server

**Date:** 2026-10-30
**Severity:** High (verification lies; deployment appears healthy when the
server is gone)

Steps to reproduce:
1. `cd stacker-projects/bunkerweb` (cloud deployment #1420 from 2026-10-23,
   server `bunkerweb-cd58` @ 78.47.139.250, recorded in
   `.stacker/deployment-cloud.lock`)
2. `stacker status`

Expected behaviour:
Status reflects reality — or at minimum warns that the server is unreachable
/gone before printing "Deployment complete".

Actual behaviour:
`stacker status` prints `✓ Deployment #1420 — status: completed` with full
server details (name, IP, emergency SSH key) for a server that **no longer
exists**:

```
$ curl -H "Authorization: Bearer $CLOUD_API_TOKEN" \
    https://api.hetzner.cloud/v1/servers/896
{"error":{"code":"not_found","message":"server not found"}}
```

Supporting evidence:
- `ping 78.47.139.250` → 100% packet loss; TCP 22/80/443/7000 all time out.
- `stacker agent status` → `Agent: ○ offline`, heartbeat 2026-10-26, all
  containers `? unknown` — reported without explaining the server is gone.
- `stacker logs --service app` → queued forever, then "timed out (last
  status: queued)" — the agent on the dead server never picks it up.
- `stacker deployment events` → only one event ("Deployment complete"),
  no `✓ Your SSH key authorized` line, so SSH verification is impossible.

Note: this session did not delete anything (repo rule: never delete
servers); the server vanished between 2026-10-23 and 2026-10-28. Stacker
needs a server-liveness/reconciliation check (or at least surface provider
`not_found` when serving status) — current state misleads the whole
verification checklist (SKILL.md §11).

## [BUG] `stacker cloud firewall list` fails with a *configure* error

**Date:** 2026-10-30
**Severity:** Medium

Steps to reproduce:
1. `cd stacker-projects/bunkerweb`
2. `stacker cloud firewall list --server-id 896`

Expected behaviour:
A read-only listing (empty list, or a clear "server not found" notice).

Actual behaviour:
```
Error: Deployment to cloud failed: Failed to configure cloud firewall for server 896 (400):
{"message":"Hetzner firewall not found: frw-bunkerweb-cd58. No firewall attached to server 78.47.139.250 was found either"}
```
A `list` subcommand invokes a configure path ("Failed to configure...") and
even reports `Deployment to cloud failed` for a read command. It also
reveals the auto-firewall `frw-bunkerweb-cd58` was **never attached**
despite `deploy.cloud.public_ports: [80, 443, 7000]` (matches the known
"auto-firewall needs listening MQ listener" gap, SKILL.md §1).

## [BLOCKED] Cloud deploy #1420 verification: app unreachable

**Date:** 2026-10-30

The 2026-10-23 cloud deployment "completed" but its server was later deleted
(see stale-state bug above). All verification checks fail:

| Check | Result |
|---|---|
| `curl http://78.47.139.250:80/` | HTTP 000 (timeout) |
| `curl https://78.47.139.250/` | HTTP 000 (timeout) |
| `curl http://78.47.139.250:7000/` | HTTP 000 (timeout) |
| ICMP ping | 100% loss |
| Hetzner API server 896 | `not_found` |
| `stacker agent status` | offline since 2026-10-26 |

No `✓ Your SSH key authorized` event exists in `stacker deployment events`,
so per repo rules SSH checks are inconclusive and were not used as evidence.
A fresh cloud deploy (`--force-new`) was started to complete the test.

## [BUG] Template port/env contract does not match bunkerity/bunkerweb:1.6.17 — app unreachable

**Date:** 2026-10-30
**Severity:** High (deployment "succeeds", app is dead at every declared port)

Steps to reproduce:
1. `stacker deploy --target cloud --key htz-0 --force-new` (deployment #1520,
   server `bunkerweb-202d` @ 78.47.139.250 — infrastructure all green:
   `✓ Your SSH key authorized`, agent online, 4 containers running).
2. `curl http://78.47.139.250:7000/` (also :80 and :443).

Expected behaviour:
HTTP response at the ports declared in `stacker.yml` (`80:80/tcp`,
`443:443/tcp`, `7000:7000/tcp`), and a healthy container
(`healthcheck: CMD curl -fs http://localhost:7000/health`).

Actual behaviour:
Connection refused on 80/443/7000; container `project-app-1` is
**unhealthy**; docker-proxy accepts and RSTs because nothing listens on the
mapped container ports.

The image's real contract (`/etc/nginx/variables.env` inside the container):

| Fixture assumes | Image actually has |
|---|---|
| `ports: 80:80` | `HTTP_PORT=8080` (nginx `default_server`, answers 503 until configured) |
| `ports: 443:443` | `HTTPS_PORT=8443` |
| `ports: 7000:7000` + `API_HOST`/`API_PORT: 7000` | `API_HTTP_PORT=5000` (api.conf, `0.0.0.0:5000`; `API_LISTEN_IP`, `API_WHITELIST_IP=127.0.0.0/8` are the real vars — `API_HOST`/`API_PORT` are **not BunkerWeb settings** and are silently ignored) |
| web UI running | `USE_UI=no` — the UI process never starts (`/var/run/bunkerweb/ui.pid` absent; ps shows only nginx) |
| healthcheck `curl localhost:7000/health` | health endpoint is `GET /healthz` on `127.0.0.1:6000` (returns `loading`/`ok`); the UI ships its own helper `/usr/share/bunkerweb/helpers/healthcheck-ui.sh` |

In-container evidence (`netstat`, nginx `listen` directives):
```
listen 0.0.0.0:8080 default_server;   # HTTP
listen 0.0.0.0:5000 reuseport;         # API (api.conf, server_name bwapi)
listen 127.0.0.1:6000;                 # healthcheck (healthcheck.bunkerweb.io)
```
`curl 127.0.0.1:8080/` → 503 (default vhost, no SERVER_NAME configured);
nothing on 80/443/7000.

Logs / Evidence:
- `docker inspect project-app-1` → `health=unhealthy`
- `ss -tlnp` on server: docker-proxy listens on host 80/443/7000, forwarded
  to container ports with no listener → external `Connection refused`.
- Agent: `project-app-1 ▶ running` (state ≠ health), `stacker agent health`
  shows no health verdict.

Proposed fix (fixture `stacker.yml`, pending user approval):
- `app.environment`: drop `API_HOST`/`API_PORT` (no-ops); add
  `HTTP_PORT: "80"`, `HTTPS_PORT: "443"`, `USE_UI: "yes"` (and if the UI's
  hard-coded port isn't 7000, remap `7000:<ui-port>` accordingly).
- `app.healthcheck.test`: `CMD /usr/share/bunkerweb/helpers/healthcheck-ui.sh`
  (official helper) or `CMD curl -fs http://127.0.0.1:6000/healthz`.
- `config_contract`: replace bogus fields (`POSTGRES_DB` on redis,
  `API_HOST`/`API_PORT`) with the real ones (`HTTP_PORT`, `HTTPS_PORT`,
  `USE_UI`, `API_HTTP_PORT`, `API_LISTEN_IP`).

## [BUG] Auto-firewall publishes loopback-bound ports to 0.0.0.0/0

**Date:** 2026-10-30
**Severity:** Medium (defense-in-depth; not directly exploitable here)

Steps to reproduce:
1. Deploy bunkerweb with `deploy.cloud.public_ports: [80, 443, 7000]` and a
   service binding redis as `127.0.0.1:6379:6379`.
2. `stacker cloud firewall list --server-id 943`

Expected behaviour:
Firewall rules only for genuinely public ports (80/443/7000/22).

Actual behaviour:
```
Rules:
- in 7000/tcp from 0.0.0.0/0
- in 80/tcp from 0.0.0.0/0
- in 6379/tcp from 0.0.0.0/0      <- redis, explicitly bound to 127.0.0.1
- in 443/tcp from 0.0.0.0/0
- in 22/tcp from 0.0.0.0/0
```
The auto-firewall derives rules from every compose port, ignoring the
`127.0.0.1:` bind restriction. Redis is unreachable in practice (docker-proxy
is bound to loopback), but the provider firewall should not open it anyway.

## [BUG] `--force-rebuild` on cloud target provisions a NEW server; reuse needs `--server`

**Date:** 2026-10-30
**Severity:** Medium (unexpected cost/side effects; doc mismatch)

Steps to reproduce:
1. A cloud deployment exists with `.stacker/deployment-cloud.lock`
   (server `bunkerweb-202d` @ 78.47.139.250).
2. `stacker deploy --target cloud --key htz-0 --force-rebuild`

Expected behaviour:
Per SKILL.md §15 ("Redeploy with updated compose (existing server):
`stacker deploy --target cloud --key=htz-0 --force-rebuild`") the existing
locked server is reused.

Actual behaviour:
Deployment #1521 provisioned a **new** server (`bunkerweb-070d` @
178.105.245.203) — phase log went straight to "Creating server
infrastructure". Reuse only happened when passing the server name
explicitly:

```
stacker deploy --target cloud --key htz-0 --server bunkerweb-070d --force-rebuild
# → "Looking up server 'bunkerweb-070d'... Found server ... (id=944)"
# → "Connecting server ..." (no infrastructure creation)
```

Either the CLI should honour the lock by default on redeploy, or SKILL.md §15
must document `--server <NAME>` as mandatory for reuse. As is, every
"redeploy" silently burns a new Hetzner server (and per repo policy servers
are never deleted).

**Resolution note for the template-contract bug above (2026-10-30):** fixed
in this session's `stacker.yml` edit (image switched to
`bunkerity/bunkerweb-all-in-one:1.6.17`, ports `80:8080`/`443:8443`/`7000`,
official healthcheck helper) — verified healthy; see
`CLOUD_DEPLOY_SUCCESS.md`.
