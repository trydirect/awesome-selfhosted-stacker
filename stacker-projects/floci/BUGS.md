# floci — known issues

## [BUG] Healthcheck runs `curl`, which is not in `floci/floci:nightly`

**Date:** 2026-11-02
**Severity:** Medium (container permanently `unhealthy` despite the app serving fine)

Steps to reproduce:
1. `stacker deploy --target local`
2. `docker inspect floci-app-1 --format '{{json .State.Health.Log}}'`

Expected behaviour:
`CMD curl -f http://localhost:4566/_floci/health || exit 1` succeeds once the
API is up (it serves HTTP 200 from the host).

Actual behaviour:
Every check fails:
```
exit 1 | /bin/sh: line 1: curl: command not found
```
`docker exec floci-app-1 command -v curl` → absent. Container shows
`Up (unhealthy)` forever. Fix: use a tool present in the image (e.g. a
python/urllib one-liner or the image's own binary) or drop the custom
healthcheck and let the image's default stand.

## [BUG] `FLOCI_HOSTNAME`/`FLOCI_BASE_URL`/`FLOCI_ENDPOINT` use DNS name `floci`, but the compose service is `app`

**Date:** 2026-11-02
**Severity:** High (UI cannot reach the API at all)

Steps to reproduce:
1. Deploy (local or cloud) and run inside the network:
   `getent hosts floci` / `getent hosts app`

Expected behaviour:
`http://floci:4566` resolves (the template sets `FLOCI_BASE_URL:
http://floci:4566`, `FLOCI_HOSTNAME: floci`, and floci-ui's
`FLOCI_ENDPOINT: http://floci:4566`).

Actual behaviour:
```
DNS floci: UNRESOLVED
172.19.0.2      app
```
The generator names the app service `app` (container `floci-app-1`), so the
hostname `floci` never resolves and every UI→API call fails. The earlier
cloud verification ("UI: 200") only checked the UI shell's status code — the
shell loads while its backend calls die. Fix: point the env vars at `app`
(or add a network alias/custom service naming).

## [BUG] `FLOCI_SERVICES_DOCKER_NETWORK: floci_default` does not exist

**Date:** 2026-11-02
**Severity:** High (core feature — spawning service/lambda containers — cannot attach them)

Steps to reproduce:
1. Deploy; `docker network ls | grep floci`

Expected behaviour:
A network named `floci_default` exists for floci-spawned service containers.

Actual behaviour:
Only `floci_app-network` (the generated compose network) exists — verified
`floci_default` is absent. Any service/lambda container floci launches with
`network: floci_default` will fail with "network not found". Fix: set
`FLOCI_SERVICES_DOCKER_NETWORK: floci_app-network` (or create/alias the
network).

## Minor drift notes (2026-11-02)

- Marketplace `long_description` says image `floci/floci:latest` and UI
  "4500 (public)", but the template pins `floci/floci:nightly` and
  `deploy.cloud.public_ports` contains only `4566` — the UI is not publicly
  reachable on cloud deploys as written.
- `stacker config validate` lint: 7 empty structural fields
  (`app.dockerfile`, `proxy.config`, `deploy.compose_file`,
  `deploy.cloud.remote_payload_file`, `hooks.*` all `null`) — suggests
  `stacker config fix`. Also `[I001]` `project.identity` unset (remote
  deploys use stack_code `custom-stack`).
- `/var/run/docker.sock` is mounted **read-write** (no `:ro`) — needed for
  floci to launch service containers, but a standing risk worth documenting
  in the listing.

## [BLOCKED] Cloud deploys end `paused [internal_error]` — Stacker backend redis regression (not template-caused)

**Date:** 2026-11-02
**Deployments:** #1524 (`--force-new`) and #1525 (`--force-new`, after the
first server vanished), Hetzner nbg1 cpx22, server IP 2.31.185.50 (recycled)

Steps to reproduce:
1. `stacker deploy --target cloud --key htz-13 --force-new`

Actual behaviour:
After `✓ Your SSH key authorized` the deployment ends
`✗ Deployment #1524/#1525 ended as 'paused' [internal_error]` — while the
app layer is fully functional (4 containers up; `/_floci/health` 200; UI
200; external 200/200 on :4566 and :4500).

Real cause — backend install-service log (provided by the maintainer,
2026-11-02 17:26), attributed to a **recent `redis_password` fix**:

```
[ERROR] 'NoneType' object has no attribute 'decode' [ServerInfo.py:54 in get_from_cache()]
  cache_output = cache.get(key).decode('utf-8')   # cache.get(key) returns None
[WARNING] ⚠️ Could not find any cached output from ansible!
[ERROR] Could not get IP from redis [watchers.py:892 in install()]
  server_ip = info.get_main_server_ip()
  app.tfa.ServerInfo.ServerInfoException: Could not get IP from redis
```

The ansible-written server-info cache is never found (redis auth change?),
so `execute_tf` cannot resolve the server IP and the install watcher fails
into the generic `paused [internal_error]` wrapper (stacker#241 hides the
cause from `stacker status`). Being investigated by the maintainer in
another session; until fixed, redeploys will pause the same way.

Observations recorded during the attempts:
- Server from deployment #1524 (`floci-25ab`) was **deleted from Hetzner**
  between checks (~30 min after serving 200/200); the platform itself
  reported "Connected cloud server 'floci-25ab' no longer exists in
  Hetzner". This session never deletes servers. IP 2.31.185.50 was then
  recycled to deployment #1525 (stale `known_hosts` refreshed).
- The `curl`-missing healthcheck bug above is real (container reports
  `(unhealthy)`) but was **not** the cause of the pause — initially
  suspected here, retracted once the backend traceback surfaced.
- `deploy.cloud.public_ports: ['4566']` notwithstanding, the auto-firewall
  also opened `4500` (same over-broad behavior as the bunkerweb 6379
  finding) — both ports were externally reachable.

**Resolution (2026-11-02):** the maintainer fixed the backend redis
regression; deployment #1526 (`--server floci-1025` reuse on
2.31.185.50) completed cleanly — `✓ Your SSH key authorized`, agent
online, external 200/200 on :4566 and :4500. See
`CLOUD_DEPLOY_SUCCESS.md`. (Deployment completed despite the broken curl
healthcheck, confirming it was never the pause cause.)
