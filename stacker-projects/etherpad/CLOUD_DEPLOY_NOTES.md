# etherpad — Cloud Deploy Notes (NPM proxy)

**Target:** cloud (Hetzner, fresh server via `htz-0`), `proxy.type:
nginx-proxy-manager`
**Date:** 2026-08-22
**Deployment:** #801, server etherpad-5b59 (id 564), real IP 128.140.34.9

## Outcome: app deployed & serving; NPM proxy step failed (self-conflict)

Root cause established from the full raw tfa/ansible log (provided by
maintainer), NOT from the stacker CLI (which mis-reported it — see #241).

### What succeeded
- Server created fine: `hcloud_server... Creation complete [id=163171115]`,
  IP 128.140.34.9. (`stacker status` showing `10.0.0.0` is just the
  private-subnet address — a #241 reporting artifact, not a real
  IP-assignment failure.)
- **Config files deployed normally**: `Staged 3 deploy-time config file(s)`
  (docker-compose.yml + 2× .env copied to the server). The config-bundle /
  bind-mount pipeline works on cloud.
- App stack deployed and runs: `curl http://128.140.34.9:9001/` → 200.

### What failed — NPM self-conflict (stacker defect, SKILL.md §10)
```
TASK [nginx_proxy_manager : Check for conflicting public port listeners]
fatal: rc: 42  PRECHECK_PORT_CONFLICT
Required ingress ports 80, 443, or 81 are already occupied.
docker_ps: project-nginx-1  0.0.0.0:80->80, 0.0.0.0:443->443
```
With `proxy.type: nginx-proxy-manager`, stacker (a) injects a
`proxy-manager` (jc21/nginx-proxy-manager) service on 80/443/81 into the
app compose, deployed by the `custom` role, AND (b) the backend runs the
separate `nginx_proxy_manager` role which deploys NPM again + runs a
port preflight. The preflight finds 80/443/81 already taken by the
app-compose proxy-manager → rc=42 → deploy fails. NPM effectively
self-conflicts (deployed twice). Matches the documented SKILL.md §10 "NPM
proxy-manager preflight false positive".

(In this specific run the conflicting container was a stale plain `nginx`
because the cloud deploy reused a compose from an earlier `proxy.type:
nginx` local run — I omitted `--force-rebuild`. But regenerating with
`--force-rebuild` produces a `proxy-manager` service on 80/443/81, which
trips the SAME preflight — so `--force-rebuild` does not fix it.)

### Mis-reporting (#241)
The real error is a clear `PRECHECK_PORT_CONFLICT rc=42` ansible failure,
but `stacker status` showed a truncated `hcloud_server... unclassified
internal error`. The whole point of stacker#241.

## Workaround (per SKILL.md §10)
Deploy with `proxy: none` and configure NPM manually, OR fix the
double-deploy/preflight ordering upstream. Not re-filed (already §10).
