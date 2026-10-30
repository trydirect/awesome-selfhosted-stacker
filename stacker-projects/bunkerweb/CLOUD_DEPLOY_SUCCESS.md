# bunkerweb — Cloud Deploy Success

**Date:** 2026-10-30
**Stacker:** 0.3.4 (6123cee), target: fresh Hetzner cloud (cpx22, fsn1)
**Server:** bunkerweb-070d (id=944) @ 178.105.245.203
**Template:** stacker.yml (image `bunkerity/bunkerweb-all-in-one:1.6.17` + redis:7.4-alpine)
**Deployment:** #1522 (first run on this server: #1521; #1520 on the earlier
server bunkerweb-202d @ 78.47.139.250 — see BUGS.md)

## Template fix applied (user-approved, required for a working deploy)

The fixture as committed could never serve traffic: it pinned the
data-plane-only image `bunkerity/bunkerweb:1.6.17` with wrong port/env
contract (see the `[BUG] Template port/env contract` entry in BUGS.md).
Fixed to match upstream `misc/integrations/all-in-one.yml`:

- `app.image` → `bunkerity/bunkerweb-all-in-one:1.6.17` (bundles
  nginx + scheduler + web UI in one container)
- `app.ports` → `80:8080/tcp`, `443:8443/tcp`, `443:8443/udp` (HTTP/3),
  `7000:7000/tcp` (web UI)
- `app.environment` → `API_WHITELIST_IP: 127.0.0.0/8`, `USE_REDIS: "yes"`,
  `REDIS_HOST`/`REDIS_PORT` (removed the no-op `API_HOST`/`API_PORT`)
- `app.volumes` → `bunkerweb_data:/data` (upstream state dir)
- `app.healthcheck.test` → `CMD /usr/share/bunkerweb/helpers/healthcheck-ui.sh`
  (official helper; replaces `curl localhost:7000/health`, which never existed)
- `config_contract` cleaned up (removed `POSTGRES_DB`-on-redis and the
  healthcheck-internal pseudo-fields), `deploy.cloud.public_ports` += `443/udp`

## Commands

```bash
cd stacker-projects/bunkerweb
./scripts/generate-secrets.sh        # no secrets needed; creates .env
export BASE_PATH=/Users/vasilipascal/work/stacker-project-examples

# deployment #1521 — fresh server (infrastructure)
stacker deploy --target cloud --key htz-0 --force-rebuild
# deployment #1522 — fixed template, reused server (no new provisioning)
stacker deploy --target cloud --key htz-0 --server bunkerweb-070d --force-rebuild
```

## Verification

| Check | Result |
|---|---|
| `✓ Your SSH key authorized (...stacker-project-test.pub)` | present (deploy log, both runs) |
| `stacker agent status` | ● online; `project-app-1` + `project-redis-1` running |
| `docker inspect project-app-1` | `health=healthy` (official `healthcheck-ui.sh`) |
| In-container components | `supervisord.pid`, `nginx.pid`, `scheduler.pid`, `ui.pid` all present |
| `curl http://178.105.245.203/` | 301 → https (HTTP→HTTPS redirect) |
| `curl -L http://178.105.245.203/` | **200** at `https://178.105.245.203/setup` |
| `curl https://178.105.245.203/` | 302 → `/setup` (HTTP/2, TLS up) |
| `curl http://178.105.245.203:7000/` | 303 → `/setup` (web UI direct) |
| `/setup` page | first-run setup wizard ("Setup" title, multi-step JS form) |

Expected first-run state: BunkerWeb serves its **setup wizard** until an
admin account is created and a `SERVER_NAME` is configured — 30x redirects
to `/setup` and (pre-config) the default vhost are the product's correct
behavior for a fresh install.

Notes:
- The setup form is JavaScript-rendered (the only static form on the page is
  the newsletter widget) — no static POST to exercise with curl; basic
  interaction beyond GET/redirect checks would need a browser. Noted as a
  stacker-QA tooling gap rather than a template bug.
- External port reachability confirmed from outside the server
  (80/443/7000 are in `deploy.cloud.public_ports` + firewall rules).
- Server left running (servers are never deleted). The existing-server phase
  deploys to the older spare server `bunkerweb-202d` @ 78.47.139.250.
