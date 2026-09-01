# Proxy Work — Session Journal (updated 2026-08-24)

## ✅✅ CADDY QA PASSED END-TO-END (deploy #818, server 579, 128.140.34.9)
`curl -H 'Host: ntfy.example.com' http://IP:80` → 200 serving ntfy. Caddy runs
once (stripped from remote compose), app on default_network, role rendered
`/home/trydirect/caddy/Caddyfile` (`http://ntfy.example.com { reverse_proxy
app:80 }`) from `stacker_proxy_domains_b64`. Full chain proven: CLI →
API Payload.proxy_domains → install AppVarsMapper (base64) → terraform
extra-vars → caddy role decode+render → routes. Took FOUR fixes: caddy admin-DB
reg, Payload threading, then base64 encoding (json-string, then base64).

## ✅✅ NPM QA PASSED END-TO-END (deploy #819, server 580, 188.245.97.117)
NPM runs once (no rc=42), app on default_network, `configure_proxy_hosts.yml`
auto-created the proxy host (['ntfy.example.com'] -> http://app:80, enabled)
via the admin API, and `curl -H 'Host: ntfy.example.com' http://IP:80` → 200
serving ntfy. Same base64 fix chain as caddy.

## 🏁 PROXY SWEEP COMPLETE — all legs green
- traefik ✅ (#803, label-based)  · caddy ✅ (#818)  · NPM ✅ (#819)
- nginx = dropped by decision (alias of NPM)
End-to-end proxy routing now works for all supported proxy types.


## ✅ TRAEFIK QA PASSED (end-to-end, live) — 2026-08-24
Deployed ntfy with `proxy.type: traefik` to a fresh cloud server (#803,
server 566, 49.12.47.82) using the rebuilt CLI:
- Deploy **completed** (no double-deploy / rc=42 — the core fix).
- Traefik runs **once** (backend role; the CLI-synthesized proxy stripped
  from the remote compose — logged "Excluding platform-managed service(s)…
  traefik").
- App carries the CLI-generated traefik labels (`traefik.enable`,
  `Host(ntfy.example.com)`, `web` entrypoint, port 80) and sits on
  `default_network` (#4).
- **Routing works:** `curl -H 'Host: ntfy.example.com' http://<ip>:80/` →
  **200**, serves ntfy's page.
- Gotcha learned: must use `--force-rebuild` after changing `stacker.yml`
  proxy config, else a stale `.stacker/docker-compose.yml` ships (first
  attempt 404'd for exactly this reason).

## ✅ SSH BACKUP-KEY BUG FIXED (verified live) — 2026-08-24
`watch_cloud_deployment` (`deploy.rs`) now saves the local backup keypair
inside its poll loop the moment the server appears in `list_servers`
(once, Cloud only) — instead of only pre-watch (fails for `--force-new`,
no server yet) and post-watch (lost on interruption). Verified on live
deploy #804: `server-567_ed25519` was on disk while status was still
`in_progress`. Compiles clean, full suite green (1797). Uncommitted in
`stacker/dev`. Minor cosmetic: a normally-completing watch now prints
"key saved" twice (both idempotent).

## ✅ DOMAIN PLUMBING DONE (contract verified locally) — 2026-08-24
`proxy.domains` now flows CLI → API → install → proxy role as the
`stacker_proxy_domains` extra-var (JSON list of `{domain, upstream, ssl}`):
- Hop 1 CLI (`stacker/src/cli/stacker_client.rs` `build_deploy_form`):
  serializes `config.proxy.domains` → `form["proxy_domains"]`. Unit-tested
  (`test_build_deploy_form_serializes_proxy_domains` + omits-when-none).
- Hop 2 API (`stacker/src/forms/project/deploy.rs`: `Deploy.proxy_domains`
  field; `stacker/src/routes/project/deploy.rs`: writes it into
  `json_request["proxy_domains"]`, mirroring `public_ports`).
- Hop 3 install (`install/app/tfa/AppVarsMapper.py`): reads
  `install_data["proxy_domains"]` → `stacker_proxy_domains` extra-var.
- Role: caddy `Caddyfile.j2` consumes it (done earlier).
Verified: stacker full suite green (1799); AppVarsMapper py_compile OK;
**seam test** — feeding the CLI's exact output shape into `Caddyfile.j2`
→ real `caddy validate` = "Valid configuration". Only a live deploy is
left to confirm runtime (install passes the extra-var → caddy role renders
→ caddy routes).

**So CADDY is now unblocked** (deploy + verify). Remaining: nginx conf.d
template (+ it consumes the same `stacker_proxy_domains`), NPM proxy-hosts
API, and committing/deploying the changes.

## ✅ NGINX + NPM ROUTING DONE (config-complete) — 2026-08-24
Both now consume the same `stacker_proxy_domains` the plumbing delivers.
- **nginx** (`roles/nginx`): new `templates/configs/stacker_proxy.conf.j2`
  renders one `server{}` per `{domain, upstream(host:port), ssl}`, reusing
  the role's `default.conf.j2` macros (proxy headers/timeouts, acme
  challenge, deny, gzip, logs). Wired into `tasks/stack.yml` → rendered to
  `configs/conf.d/stacker_proxy.conf` (nginx.conf already includes conf.d).
  Empty when no domains. **Verified**: rendered with the CLI's exact output
  shape → real `nginx -t` = "syntax is ok / test is successful". Note:
  nginx has no built-in ACME → HTTP(:80) blocks + acme webroot location;
  TLS via certbot is a separate follow-up (ssl field accepted for parity).
- **NPM** (`roles/nginx_proxy_manager`): new `tasks/configure_proxy_hosts.yml`
  — NPM has no config file (routing lives in its DB), so it drives the admin
  API: waits for :81, gets a token (default `admin@example.com`/`changeme`,
  overridable via `npm_admin_email/password` vars), lists existing hosts,
  creates a proxy host per new domain (block_exploits + websocket upgrade,
  idempotent — skips domains already present). Wired into `tasks/main.yml`
  (gated on non-portainer + non-empty domains); vars added. HTTP-only for
  now (LE issuance via NPM is async + needs DNS pointed → follow-up). All
  YAML validated.

**Per-proxy status now:** traefik ✅ done+QA'd live. caddy ✅ config-complete
(needs live deploy). nginx ✅ config-complete (nginx -t verified). NPM ✅
config-complete (proxy-host API task). All four consume `stacker_proxy_domains`.
Remaining: live QA deploys (caddy/nginx/NPM) + optional LE/TLS follow-ups
(nginx certbot, NPM LE cert request).

Uncommitted repos now: stacker/dev (deploy.rs SSH fix, config.rs validate
polish, stacker_client.rs + forms + routes proxy_domains), install
(AppVarsMapper.py), tfa/production (traefik + caddy roles).

## ⚠️ CADDY QA BLOCKED — proxy role needs admin-DB registration — 2026-08-24
Live caddy deploy #807 (project 551, server 570 @49.12.47.82) COMPLETED but
**caddy never routed** — no caddy container, nothing on :80. Root cause
(verified against the live project record + install source):
- CLI is correct: injects `extended_features:["caddy"]` + `proxy_domains`;
  the proxy is synced to the project as a plain service
  `metadata.custom.service=[{code:"caddy", role:null}]`, `feature=[]`.
- Install `get_features_roles()` collects roles from `self.stack["features"]`
  and **skips any entry with no `role`** → caddy role never collected → never
  deployed.
- traefik/nginx_proxy_manager work because they ARE registered in the
  admin/marketplace DB as proxy features WITH a role; caddy is not.
**Fix (user, admin/DB):** register caddy as a feature `code:"caddy"`,
`role:["caddy"]`. Full detail in memory [[proxy-role-activation-admin-db]].
Secondary CLI cleanup: add caddy/traefik to `PLATFORM_MANAGED_APP_CODES`
(`stacker/src/project_app/mod.rs`) to stop the junk role:null service +
orphan caddy_data/caddy_config volume decls.

Implications for the rest of the sweep:
- **NPM** (`nginx-proxy-manager`): registered already → QA should work now
  (tests my new `configure_proxy_hosts.yml`).
- **plain nginx** (`proxy.type: nginx`): CLI injects `nginx_proxy_manager`
  into extended_features for BOTH nginx and NPM, so nginx-as-proxy has NO
  distinct feature/role — it would run the NPM role, not the `nginx` role,
  and my new `nginx/.../stacker_proxy.conf.j2` would never be used. Needs a
  design decision (give plain-nginx its own proxy feature/role, or drop it).

## ⚠️ NPM QA — deploys once, but auto proxy-host NOT created — 2026-08-24
NPM deploy #810 (server 572 @167.235.204.61): nginx-proxy-manager runs ONCE
(no rc=42/double-deploy — core fix good), app on default_network. BUT routing
served NPM's "Default Site" page, not ntfy — no proxy host created (empty
data/nginx/proxy_host). My `configure_proxy_hosts.yml` API contract is PROVEN
correct: manual replay of the exact POST created proxy-host id=1 → routing then
served `<title>ntfy web</title>`. The task was SKIPPED during deploy because
`stacker_proxy_domains` was empty.

### ROOT CAUSE (shared with caddy): production Stacker API drops proxy_domains
`public_ports` + `proxy_domains` are inserted into the SAME `json_request`
(routes/project/deploy.rs ~L1448/L1466). public_ports reaches install
(works); proxy_domains does not. Only explanation: the **production Stacker
API runs pre-`1a4dfb36` code** whose `Deploy` struct lacks the `proxy_domains`
field → serde silently drops it (unknown field) before rebuilding json_request.
Deploy still succeeds; field vanishes.
**FIX (user): redeploy production Stacker API from dev HEAD `1a4dfb36`.**
Unblocks BOTH caddy (now DB-registered) and NPM routing.

Sweep status: caddy = needs API redeploy (DB reg done). nginx = dropped
(alias of NPM). NPM = deploys+API-task correct, needs API redeploy to feed
domains. All three converge on: **redeploy production Stacker API**.

## ✅ REAL ROOT CAUSE FIXED — proxy_domains was plumbed to the wrong object
Correction to the above: it was NOT merely a stale API image. The install MQ
payload is built in `install_service.deploy()` from `Payload::try_from(project)`
(= project.metadata) + call args — it NEVER reads the deployment's `json_request`
where the original hop-2 wrote proxy_domains. So proxy_domains was a dead-end
regardless of image version. (public_ports only "works" because install DERIVES
it from services' shared_ports — separate path, no top-level field.)
FIX (stacker/dev, uncommitted, lib builds + tests green 1806):
- `forms/project/payload.rs`: new top-level `Payload.proxy_domains` field
  (+ regression test `payload_serializes_proxy_domains_at_top_level`).
- install_service `mod.rs`/`client.rs`/`mock.rs`: `deploy()` gains a
  `proxy_domains` param; client sets `payload.proxy_domains = proxy_domains`.
- `routes/project/deploy.rs`: pass `form.proxy_domains.clone()`; the old
  json_request insert kept as audit-only (comment corrected).
**Next: rebuild + redeploy the stacker API image**, then re-run caddy + NPM QA.
Definitive check for this bug class = "does install_data contain proxy_domains?"
(NOT the version string — crate version is 0.3.1 on every commit).

Also done (same session, stacker/dev, uncommitted, tests green):
- **Orphan-volume prune in the strip** (`config_bundle.rs`): stripping a
  platform proxy service now also drops the named volumes only it used
  (e.g. caddy_data/caddy_config) while keeping volumes a surviving service
  still mounts + bind mounts. Test
  `strip_platform_managed_services_prunes_orphaned_named_volumes`. Full
  config_bundle suite green (15).
- **NOT done (deliberately):** adding caddy/traefik to
  `PLATFORM_MANAGED_APP_CODES`. It's used in 7 places incl. build_project_body,
  which skips services by name/image — that would wrongly strip a user's OWN
  caddy/traefik service with no `proxy:` block, violating the agreed design
  (own proxy service stays project-scoped). The synthesized proxy is already
  handled correctly via its `scope: platform` label. Left as-is.

CODE SIDE COMPLETE. Whole remaining blocker = user rebuilds+redeploys the
stacker API image (+ caddy already registered in admin DB). Then re-run
caddy + NPM QA — expect populated Caddyfile / auto-created NPM proxy-host.

## ⚠️→✅ THIRD blocker found+fixed on live retry: Terraform extra-vars = scalar strings only
After the API redeploy, live deploy #816 confirmed the API fix works:
`stacker_proxy_domains` WAS populated in the tofu extra_vars AND roles included
`caddy` (DB reg works). BUT `tofu plan` PAUSED: `servers.tf` builds
`--extra-vars 'key=value'` by string-interpolating each value → "string
required, but have tuple" because I passed proxy_domains as a native LIST.
Every tfa extra-var must be a scalar STRING (client_public_ports is a
comma-joined string, not a list). FIX (install + tfa, uncommitted, validated):
- `AppVarsMapper.py`: `json.dumps(...)` the proxy_domains → JSON string.
- caddy `Caddyfile.j2`: parse with `from_json` (guarded `is string`).
- NPM `configure_proxy_hosts.yml`: set_fact `stacker_proxy_domain_list` from
  from_json; loop uses it. `main.yml` include-gate parses before length-check
  ("[]".length==2 would misfire).
Validated: py_compile OK; Caddyfile renders from a JSON STRING → caddy validate
= Valid; empty "[]" → blank + gate False; NPM YAML OK.
Testing-gap lesson (user: "how did that pass the test?"): no test crossed the
terraform extra-vars string boundary — the seam test fed jinja a native list.
Fix seam tests to use `from_json(json.dumps(x))`.

**Next: redeploy install + tfa with these changes, then re-run caddy + NPM QA.**

# --- earlier state below ---

# Proxy Work — Session Journal (paused 2026-08-24)

Cross-repo work to fix stacker's reverse-proxy handling. Two source repos:
`~/work/try.direct/stacker` (CLI + API, Rust) and `~/work/try.direct/tfa`
(install-service Ansible roles). QA fixtures: this repo
(`stacker-project-examples`).

## The core problem (root-caused)
`proxy.type` (nginx / nginx-proxy-manager / traefik / caddy) was
**double-deploying** the proxy: the CLI synthesized the proxy as a service
in the project compose AND the backend ran a role that deployed the same
proxy in its own dir → both bound 80/443/81 → `PRECHECK_PORT_CONFLICT
rc=42` (NPM) or a docker port-bind failure (others) → deploy failed,
mis-reported as a generic `hcloud… unclassified internal error` (stacker#241).
Design (docs/APP_DEPLOYMENT.md): proxies are **platform-managed** — own
dir, backend role, NOT in the project compose ("no duplicate runtime
ownership").

## DONE — committed (trydirect/stacker, branch `dev`)
- `53262031` **Piece-1**: `build_config_bundle` strips `my.stacker.scope:
  platform` services from the compose shipped to the backend (remote only;
  local keeps the proxy). `src/cli/config_bundle.rs`.
- `b1caa5a2` **#2 W003**: `config validate` warns when a `proxy:` block +
  a service publish the same ingress host port (80/443/81). Detected by
  host-port overlap, per-service, one warning.
- `f3146225` **W001 bug fix**: `extract_host_port` returned the leading IP
  for the `ip:host:container` form → false positives (e.g. two loopback
  services on different ports flagged as sharing "port 127.0.0.1") and
  false negatives. Replaced with `host_port_binding`. `src/cli/config_parser.rs`.

## DONE — uncommitted, for review (trydirect/stacker, branch `dev`)
- **#4** (`src/cli/generator/compose.rs`): all four proxies are now
  platform-managed. `build_proxy_service` labels nginx/traefik/caddy
  `scope: platform` (NPM already did) → Piece-1 strips ALL of them on
  remote → backend role is sole owner (no double-deploy for any type).
  Also broadened the `default_network` app-wiring from NPM-only to all
  proxy types, so the backend proxy can reach the app. Tests updated + added.
- **Validate output polish** (`src/console/commands/cli/config.rs`):
  `config validate` prints `[W003] warning (proxy.type): …` instead of raw
  Debug. Added `Severity` import.
- Full lib suite green (1797 passed). Live-demoed: traefik/caddy/npm each
  stripped to `["app"]` in the remote compose, kept locally.

## DONE — uncommitted, for review (tfa, branch `production` ⚠️)
- **traefik role** (`roles/traefik/{templates/docker-compose.yml.j2,
  vars/main.yaml}`): removed `--api.insecure=true` + public :8080
  (security fix); added `websecure :443` + published :443; ACME
  `letsencrypt` resolver (conditional on email) + `traefik_certs` volume.
  Entrypoint/resolver names match the CLI's app labels. Validated via
  `docker compose config` (both email/no-email). **ACME cert issuance
  still needs `admin_email` plumbed to the role** (sourced forward-compat
  as `traefik_acme_email | admin_email | default('')`).
- **caddy role** (`roles/caddy/{tasks/stack.yml, vars/main.yaml,
  templates/Caddyfile.j2}`): generates a Caddyfile from
  `stacker_proxy_domains` (fixes the "mounts a Caddyfile it never creates"
  bug). Validated: real `caddy validate` → "Valid configuration".

## NOT DONE — the domain plumbing (the last blocker for caddy/nginx routing)
`proxy.domains` is NOT currently sent to the backend. Contract to wire:
var `stacker_proxy_domains` = JSON list of `{domain, upstream, ssl}`.
Hops (mirror how `public_ports` flows):
1. CLI `build_deploy_form` (`stacker_client.rs` ~4155) — serialize
   `config.proxy.domains` into the form (like `public_ports` at ~4285).
   *Verifiable via unit test; not started.*
2. Stacker API (`src/routes/project/deploy.rs`) — forward into the install
   payload (like `public_ports` → `client_public_ports`).
3. install `AppVarsMapper.py` (~453) — add `stacker_proxy_domains` extra-var.
4. Roles: caddy ✅ consumes it; nginx still needs a `conf.d` template.
- **NPM routing**: proxy-hosts must be configured post-deploy via NPM's
  admin API — separate, not started.

## GitHub issues filed this session
- stacker#234 (agent status/health resolve different active deployments) — fixed
- stacker#235 (local deploy shared compose project name collisions)
- stacker#238 (`--target server --dry-run` does a real docker pull) — open
- stacker#240 (`--target server` shared remote path → real data loss) — FIXED
- stacker#241 (real failure buried under generic error) — open, partially
- stacker#242 (proxy config generation unimplemented — traefik/nginx/caddy) — being fixed
- install#85 (get_deployment_failed_email missing `status`) — fixed
- stacker#219/#211/#236/#237 — all verified fixed

## What's realistically QA-able RIGHT NOW (see next section)
The **deploy-success fix** (Piece-1 + #4: no more double-deploy) is
testable with the rebuilt CLI. **Actual routing** depends on the tfa
changes being *deployed to the backend* (they're only in the local tfa
working tree, uncommitted) AND, for caddy/nginx, the domain plumbing
(not done). So:
- **NPM / any proxy**: "deploy completes (no rc=42), proxy runs once" —
  testable now with rebuilt CLI.
- **Traefik routing**: works via app labels IF the tfa traefik role change
  is deployed to the install backend (no domain plumbing needed).
- **Caddy routing**: blocked on domain plumbing (hops 1–3).

## POSTPONED bug — SSH backup key lost on interrupted `--watch` (root-caused)
`save_local_backup_keypair_early` (`deploy.rs:3664`, called at ~3621 before
the watch) early-returns when `fetch_server_for_project` finds no server yet.
For a `--force-new` cloud deploy the server is created *during* async
provisioning, so at that call point the server usually doesn't exist → no
key saved. The actual save then only happens after `watch_cloud_deployment`
returns — so if the watch is interrupted (timeout / Ctrl-C / net), the key
is never written and SSH access to a successfully-deployed server is lost.
**Fix (later):** save the keypair from *inside* the watch loop the moment
server details first appear (server id known), not gated on the pre-watch
fetch. User asked to postpone.

### Rebuilt CLI to test with
`~/work/try.direct/stacker/target/debug/stacker-cli` (has Piece-1 + #4).
The installed `/usr/local/bin/stacker` is the OLD build — use the rebuilt
one for QA.
