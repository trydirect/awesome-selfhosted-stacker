# espocrm — Cloud Deploy: BLOCKED (infra, server IP never assigned)

**Target:** cloud (Hetzner, fresh server via `htz-0`)
**Date:** 2026-08-22
**Status:** Not completed — Hetzner server provisioning fails; public IP
never assigned. Reproduced twice (servers 561, 562).

## Symptom

Three `--force-new` attempts (deployments #798, #799, #800 — the last
*after* the install#85 reporting-handler fix) all paused during
Terraform apply, consistently at:
```
hcloud_server.server[0]: Still creating... [10s elapsed] | hcloud_server.server[0
An unclassified internal error occurred. Redeploying will retry; if it keeps failing, contact support with the deployment hash.
```
`stacker servers` shows both servers with IP `10.0.0.0` (the private
subnet address) — the public IP was never assigned. Same class as the
root `BUGS.md` entry "Cloud deploy: server created but IP never assigned".

## Notable difference from working deploys this session

These espocrm deploys provision a **private network + subnet**
(`hcloud_network` + `hcloud_network_subnet` 10.0.0.0/24) before the
server — which the earlier *successful* cloud deploys this session
(duplicati #786, caddy #773, code-server #778) did not. The hang is at the
server-creation step right after that network setup, so the newer
network-provisioning path may be implicated. Infra/backend issue, not
fixable from the CLI.

## What was still verified (stacker-level)

- Config parsed and deploy form built correctly (traefik proxy, secrets,
  services all present).
- Secrets managed via `stacker secrets` (see `BUGS.md` / local success).

Blocked at the Hetzner provisioning layer, not at anything in this
project's `stacker.yml`. Per session policy, did not burn a third server.

## Root cause — CORRECTED 2026-08-22

**Earlier notes here blamed an AMQP `ConnectionLostError` / "server IP
never assigned". That was wrong** — corrected after the maintainer
provided the full raw tfa log for a sibling deploy (etherpad #801). Key
learning: the `10.0.0.0` IP + `hcloud_server... unclassified internal
error` shown by `stacker status` is a **reporting artifact** (stacker#241)
— it surfaces the terraform hcloud trace and buries the real ansible
error. The server is actually created fine; the real failure is later, in
an ansible task.

For **espocrm specifically, the real cause is UNCONFIRMED** — no raw tfa
log was captured for #798-800. Do NOT assume it's AMQP or identical to
etherpad. Given espocrm used `proxy.type: traefik`, a proxy-related
preflight/ansible failure (mis-reported the same way) is plausible but
unverified. `get_deployment_failed_email` handler crash
([install#85](https://github.com/trydirect/install/issues/85)) is a real
backend bug found in the logs, but it's the failure-*reporting* path, not
necessarily espocrm's failure *cause*.

Bottom line: espocrm cloud is held as blocked pending a real per-deploy
tfa log to identify the actual cause. Not retrying further per user
direction.

## Positive note on error surfacing

Unlike the `--target server` failures (opaque `local-exec provisioner
error`), this cloud/Terraform failure DID surface a useful chunk of the
real TF apply trace in `stacker status` — see comment on stacker#241.
