# Stacker Deploy Pipeline Knowledge

## Overview

Stacker deploys containerised apps to cloud (Hetzner) via a multi-step pipeline:

```
stacker.yml → CLI → Stacker API → MQ → Install Service (Terraform + Ansible) → Cloud Server
```

This document captures known issues, fixes, and best practices discovered while
deploying the 65+ apps in this repo to local, own-server, and Hetzner cloud
targets. Every section is grounded in a real deployment that broke and how it
was fixed.

---

## Contents

1. [Port Publishing (`public_ports`)](#1-port-publishing-public_ports)
2. [Image Tag Preservation (`dockerhub_tag`)](#2-image-tag-preservation-dockerhub_tag)
3. [Cloud Deploy Requires `app.image`](#3-cloud-deploy-requires-appimage)
4. [Database Initialisation](#4-database-initialisation)
5. [Secure Project Pattern](#5-secure-project-pattern)
6. [Template Variables (`install.inputs`)](#6-template-variables-installinputs)
7. [`command` and `healthcheck` Support](#7-command-and-healthcheck-support)
8. [Known Project-Specific Issues](#8-known-project-specific-issues)
9. [Config Bundle / Bind Mount Pipeline](#9-config-bundle--bind-mount-pipeline)
10. [Port Conflict Validation](#10-port-conflict-validation)
11. [Deployment Verification Checklist](#11-deployment-verification-checklist)
12. [Common Failure Patterns](#12-common-failure-patterns)
13. [Config Pipeline (Rust Source Map)](#13-config-pipeline-rust-source-map)
14. [Testing](#14-testing)
15. [Deploy command reference](#15-deploy-command-reference)
16. [Hooks — Execution & Safety](#16-hooks--execution--safety)
17. [Secrets: Vault-backed vs `.env`](#17-secrets-vault-backed-vs-env)
18. [Status Panel Agent — Daemon Mode & Pipe Execution](#18-status-panel-agent--daemon-mode--pipe-execution)

---

## 1. Port Publishing (`public_ports`)

### Where to set it

```yaml
deploy:
  target: cloud
  cloud:
    provider: hetzner
    region: fsn1
    size: cpx22
    public_ports:
      - "8080"
      - "8053/tcp"
      - "8053/udp"
```

### How it flows

1. **CLI** (`src/cli/config_parser.rs`): `CloudConfig` has `public_ports: Vec<String>`
2. **CLI** (`src/cli/stacker_client.rs`): `build_deploy_form` injects `public_ports` into deploy request JSON
3. **API** (`src/forms/project/deploy.rs`): `Deploy` struct accepts `public_ports`
4. **Deploy handler** (`src/routes/project/deploy.rs`): `execute_deployment` stores `public_ports` in
   deployment metadata (`row.request_json`)

### Auto-firewall trigger points

| Trigger | Location | When | Condition |
|---|---|---|---|
| Existing server redeploy | `deploy.rs:1449` | After `install_service.deploy()` | Server has `srv_ip` |
| New deployment completes | `listener.rs:474` | MQ listener receives "completed" | Deployment metadata has `public_ports` |

### Port format

| Format | Protocol | Example |
|---|---|---|
| `"8080"` | TCP (default) | Web admin |
| `"8000/tcp"` | TCP (explicit) | App HTTP |
| `"53/udp"` | UDP | DNS |
| `"8053/tcp"` | TCP on alt port | Pihole DNS workaround |

### Correction (2026-08-20): auto-detection can cover missing `public_ports`

Tested with `caddy` (no `deploy:`/`deploy.cloud` section in `stacker.yml`
at all — no `provider`, `region`, `size`, or `public_ports`): cloud deploy
still auto-opened `80/tcp` and `443/tcp` correctly, derived from
`app.ports` (`"80:80"`, `"443:443"`, `"443:443/udp"`). So the "without
`public_ports`, only SSH is open" warning above isn't universal — don't
assume a project needs an explicit `public_ports` list just because
`stacker.yml` lacks one; check `stacker cloud firewall list --server-id
<id>` after deploy before concluding ports are closed.

### Known issue: auto-firewall needs listening MQ listener

The auto-firewall only works when `stacker listener` (MQ consumer) is running.
Without it, the "completed" status never triggers the firewall configuration.
Manual fallback:

```bash
stacker cloud firewall add --public-ports 8000/tcp [--server-id <ID>]
```

---

## 2. Image Tag Preservation (`dockerhub_tag`)

### Root cause

The server-side `DockerImage` struct (`src/forms/project/docker_image.rs`) was missing
a `dockerhub_tag` field. The CLI correctly parses `postgres:15-alpine` into
`dockerhub_name=postgres` + `dockerhub_tag=15-alpine`, but when the JSON reached the
server, `dockerhub_tag` was silently dropped (not in the struct). The `Display` impl
then fell back to `:latest` for any image without an inline tag.

### Fix

Added `pub dockerhub_tag: Option<String>` to `DockerImage`. The `Display` impl now
prefers the detached tag over the `:latest` fallback. The `build_project_body` path
(CLI → server) correctly preserves version pins from `stacker.yml` into the DB.

### Impact

Every project using postgres on cloud deploy **was** affected (plausible, umami,
ghost, outline, supabase, etc.). After server rebuild, tags are preserved through
the full pipeline.

### Workaround (no server rebuild)

```bash
stacker secrets apps sync --project <name>
```

This bypasses `DockerImage` entirely, sending the raw `image:` string directly
to `POST /project/{id}/apps`.

---

## 3. Cloud Deploy Requires `app.image`

### Rule

Cloud deploys **must** use `app.image`. `app.dockerfile` only works for local
deploys because the remote server can't build from source.

```yaml
# ✅ Cloud-compatible
app:
  image: archivebox/archivebox:latest

# ❌ Local-only — won't work on cloud
app:
  dockerfile: Dockerfile
```

When converting a project from `dockerfile` to `image`, find the public image
on Docker Hub or GHCR (e.g., `ghcr.io/umami-software/umami:postgresql-latest`,
`archivebox/archivebox:latest`).

---

## 4. Database Initialisation

### Postgres

Add `POSTGRES_DB` and `POSTGRES_USER` env vars to the postgres service so the
database is auto-created on first start:

```yaml
services:
  - name: plausible_db
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: "${DB_PASSWORD}"
      POSTGRES_DB: plausible
```

Without `POSTGRES_DB`, the app container fails with:

```
FATAL 3D000 (invalid_catalog_name) database "plausible" does not exist
```

### ClickHouse

Mount an init SQL script at `/docker-entrypoint-initdb.d/`:

```yaml
volumes:
  - ./init-clickhouse.sql:/docker-entrypoint-initdb.d/init.sql
```

Where `init-clickhouse.sql`:
```sql
CREATE DATABASE IF NOT EXISTS plausible;
```

### Generic pattern

For apps needing a one-time setup (ArchiveBox: `archivebox init`, Django:
`manage.py migrate`), use `command:` on the `app:` section:

```yaml
app:
  command: >-
    sh -c "./manage.py migrate && ./manage.py runserver 0.0.0.0:8000"
```

This is now supported on both `AppSource` and `ServiceDefinition`. The `command`
field survives the config renderer pipeline (DB → Vault → agent compose).

---

## 5. Secure Project Pattern

Every reusable stacker project should follow this layout:

```
project/
  .env.example           # Template with empty secrets — COMMITTED
  .env                   # Actual secrets — GITIGNORED
  .gitignore             # Protects .env and .stacker/
  scripts/
    generate-secrets.sh  # Idempotent — fills empty keys with openssl rand
  stacker.yml            # Main config
```

### stacker.yml skeleton

```yaml
name: myproject
version: "1.0.0"

project:
  identity: myproject

app:
  type: custom
  image: owner/myproject:latest
  environment:
    DATABASE_URL: "postgres://user:${DB_PASSWORD}@postgres:5432/db"

services:
  - name: postgres
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: "${DB_PASSWORD}"
    healthcheck:
      test: "CMD-SHELL pg_isready -U postgres"
      interval: 5s
      timeout: 2s
      retries: 10

install:
  inputs:
    commonDomain: myproject.example.com

config_contract:
  services:
    postgres:
      secret: [POSTGRES_PASSWORD]
    app:
      secret: [DB_PASSWORD]

hooks:
  pre_build: ./scripts/generate-secrets.sh

env_file: .env
```

### generate-secrets.sh template

```bash
#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ ! -f .env ] && cp .env.example .env

need() {
  local val
  val=$(grep "^$1=" .env 2>/dev/null | cut -d= -f2- || true)
  [ -z "$val" ]
}

if need "DB_PASSWORD"; then
  set_secret "DB_PASSWORD" "$(openssl rand -hex 16)"
fi
# ... repeat for each secret
```

**Portability:** GNU `sed -i` and BSD/macOS `sed -i ''` are incompatible, and
base64 secrets contain `/` which breaks a `/`-delimited `sed` (see §8). Use a
helper that sidesteps both — works on Linux hooks and macOS dev machines:

```bash
set_secret() {  # $1=key  $2=value
  local key="$1" val="$2"
  if [ "$(uname)" = "Darwin" ]; then
    sed -i '' "s|^$key=.*|$key=$val|" .env
  else
    sed -i "s|^$key=.*|$key=$val|" .env
  fi
}
```

### .env.example template

```
# Copy to .env and generate secrets before first deploy:
#   cp .env.example .env && ./scripts/generate-secrets.sh

# Public config
PUBLIC_VAR=default_value

# Secrets (generated by ./scripts/generate-secrets.sh)
DB_PASSWORD=
SECRET_KEY_BASE=
```

---

## 6. Template Variables (`install.inputs`)

Stacker supports injecting dynamic values at deploy time:

```yaml
install:
  inputs:
    commonDomain: myapp.example.com   # Special: auto-injected into deploy form
    plan: pro                         # Becomes a stack var: {key: "plan", value: "pro"}
```

### CLI overrides

```bash
stacker deploy --domain myapp.example.com     # sets commonDomain
stacker deploy --set plan=pro                # sets any input key
stacker deploy --set admin_email=a@b.com     # multiple --set allowed
```

### Key normalisation

`domain` and `base_domain` input keys are automatically mapped to `commonDomain`.

### Default

If not set, `commonDomain` defaults to `{sanitized_project_name}.example.com`.

### What they should NOT contain

`install.inputs` values are sent to the server as stack vars and stored in the DB.
Use them only for non-sensitive config (domains, emails, plan names). Secrets
must use `${ENV_VAR}` references that resolve from `.env` at deploy time.

---

## 7. `command` and `healthcheck` Support

Both are now available on `AppSource` and `ServiceDefinition`:

```yaml
app:
  command: >-
    sh -c "init.sh && start.sh"

services:
  - name: postgres
    image: postgres:16-alpine
    healthcheck:
      test: "CMD-SHELL pg_isready -U postgres -d mydb"
      interval: 5s
      timeout: 2s
      retries: 10

  - name: redis
    image: redis:7-alpine
    command: redis-server --requirepass "${REDIS_PASSWORD}"
    healthcheck:
      test: "CMD-SHELL redis-cli -a ${REDIS_PASSWORD} ping | grep PONG"
      interval: 5s
      timeout: 2s
      retries: 10
```

These fields survive the config renderer pipeline (parser → compose gen →
DB → Vault → agent compose).

### Type note

`retries` must be an unquoted integer (`retries: 10`), not a string
(`retries: "10"`). The latter causes a parse error since `ComposeHealthcheck.retries`
is `u32`.

---

## 8. Known Project-Specific Issues

| Project | Issue | Fix |
|---|---|---|
| **pihole** | Port 53 taken by systemd-resolved | Use `8053:53/udp` + `8053:53/tcp` |
| **coolify** | `command`/`healthcheck` support needed for redis + postgres | Now available on `ServiceDefinition` as of the compose pipeline update |
| **plausible** | DB not auto-created, `command:` overwritten by config renderer | Add `command:` to `app:` in stacker.yml — it now survives config rendering |
| **supabase** | 10+ services, complex | `config_contract` declares all required/secret vars per service |
| **dify** | `orchestrator: remote` | Uses marketplace deploy path, not standard CLI |
| **AstrBot** | `stacker.yml` was template placeholder `<stacker.yml content here>` | Created from official compose |
| **swarm-ui** | No `stacker.yml` at root, misconfigured subdirectory | Created proper config at project root with ports/volumes |
| **All projects** | `healthcheck.retries: "10"` (string) caused parse error | Must be unquoted integer: `retries: 10` |
| **archivesspace** | Requires one-time `setup-database.sh` on first deploy | Add `app.command:` or run `docker exec ... /archivesspace/scripts/setup-database.sh` |
| **All projects** | `generate-secrets.sh` sed delimiter bug — `-base64` output contains `/` which breaks sed's `/` delimiter, corrupting `.env` values | Use `|` delimiter: `sed -i "" "s|^KEY=.*|KEY=$(openssl rand -base64 32)|" .env` |
| **shlink** | `${VAR:-default}` bash-style default syntax in `app.environment` is NOT supported — stacker's substitution only handles bare `${VAR_NAME}` and errors on the literal string including `:-` | Use plain `${VAR}` and define the key (even empty) in `.env`/`.env.example` |
| **All local deploys** | `--target local` uses a hardcoded, unnamespaced Compose project name (`stacker`) — deploying project B can recreate/destroy project A's running local containers, and generic volume names (e.g. `postgres_data`) collide across projects, silently reusing stale DB data with the wrong credentials ([stacker#235](https://github.com/trydirect/stacker/issues/235)) | If a freshly-deployed service fails DB auth (`role "x" does not exist`) right after a *different* project was deployed locally, suspect volume collision first — check `docker volume ls \| grep stacker_`, `docker volume rm stacker_<name>`, redeploy |

---

## 9. Config Bundle / Bind Mount Pipeline

### Overview

Config files (`.env`, `config.yaml`, etc.) referenced in `app.volumes` bind mounts are
collected into a config bundle (`config-bundle.tar.zst`) and shipped to the remote server.
The bundle is stored under `.stacker/deploy/<environment>/`.

### Pipeline

```
stacker.yml (app.volumes) → build_config_bundle() → tar.zst archive + manifest
→ attach to deploy form (config_files + config_bundle fields)
→ Stacker API → MQ → Install Service extracts files → compose references rewritten
```

### Bug 1: Environment Gate (fixed)

**Root cause:** `build_config_bundle` at `deploy.rs:3266` was gated on
`selected_environment` being `Some`. Without `deploy.environment` + `environments:`
block (or `--env` flag), `config_bundle` was `None` and no config files were collected.

**Manifestation:** `config_files=[]` in Install Service Ansible/Terraform command for
every deployment without an environment configured.

**Fix (#1):** Removed the environment gate. `build_config_bundle` now uses `"default"`
as the environment name when none is configured. Added `reference_base: &Path` parameter
so the caller specifies path resolution semantics:
- Generated compose (`.stacker/…`): resolve against `project_root`
- User-supplied compose: resolve against the compose's own parent directory

### Bug 2: `./` Prefix Stripped from Bind Mount Sources (fixed)

**Root cause:** `collect_reference` in `config_bundle.rs:368` returned
`destination_path` (e.g., `config.yaml`) without the `./` prefix. When
`rewrite_volumes` at `config_bundle.rs:318` substituted it back into the volume spec,
the result was `config.yaml:/etc/d8a/config.yaml:ro` — Docker treats bare names as
**named volumes**, not bind mounts.

**Manifestation:** Container started but the config file was not mounted. Docker created
an empty named volume "config.yaml" instead.

**Fix (#2):** `collect_reference` now re-adds `./` prefix when the original reference
started with `./`:
```rust
if reference.starts_with("./") && !dest.starts_with("./") {
    dest.insert_str(0, "./");
}
```

### Verification

1. Deploy must show "Config bundle:" with collected files
2. Remote compose must have `./` prefix on bind mount sources: `./config.yaml:`
3. `docker inspect` should show `Type: bind` for the mount
4. File content must be readable inside the container

### Out of scope

The same `.stacker/`-vs-project-root path mismatch affects local `docker compose up`
on the generated compose — `normalize_generated_compose_paths` doesn't rewrite volume
sources the way it rewrites `build.context`. If local deploys fail with missing bind
mount files, extend `normalize_generated_compose_paths` to rewrite volume sources too.

### CRITICAL: `--target server` shares ONE remote path across every project (2026-08-20)

The same unnamespaced-project-name bug as #235 (local `--target local`) also hits
the **remote** `--target server` path, and it's more dangerous because the target
server may host other people's real, working deployments. Every project deployed
via `--target server` to the same host writes to the **exact same**
`/home/trydirect/project/docker-compose.yml` (and `.env`), unconditionally
overwriting whatever was there — confirmed by deploying `duplicati` to the shared
`EXISTING_SERVER_HOST` right after a pre-existing `rallly` deployment was already
running there: `duplicati`'s deploy reported "completed" but the compose file on
disk still showed rallly's config, and rallly's `app`+`db` containers were left
crash-looping (compose-file thrashing between the two projects' definitions).

**Do not casually run `--target server` against a shared/multi-tenant host** —
first check `ls -la /home/trydirect/` (or wherever the target's deploy path is) for
existing project directories, and treat any occupied host as carrying real risk to
whatever's already deployed there. When testing this repo's projects against a
shared box, prefer provisioning a fresh dedicated server per testing session
(`stacker deploy --target cloud --force-new` against any project, then
`stacker config setup server --ip <new-ip>` to register it) over reusing a
long-lived shared `EXISTING_SERVER_HOST` that may carry other real deployments.

---

## 10. Port Conflict Validation

Stacker validates that two services don't bind the same host port. This
validation is now protocol-aware: `8053/tcp` and `8053/udp` are treated as
different ports.

The fix is in `extract_host_port_from_string` (`deploy.rs:1626`): the protocol
suffix (e.g., `/tcp`, `/udp`) is now included in the extracted host port,
preventing false conflicts when the same host port is used for both protocols.

### Proxy architecture & the NPM double-ownership regression (deep analysis 2026-08-23)

**Design (docs/APP_DEPLOYMENT.md, confirmed with maintainer):** a proxy
declared via the **`proxy:` block** (`proxy.type: nginx|nginx-proxy-manager|
traefik|caddy`) is **platform-managed** — it lives in its OWN dir
(`/home/trydirect/{nginx_proxy_manager,traefik,caddy}/`), is deployed by a
**backend ansible role**, and must **NOT** appear in the project compose.
The convention exists explicitly "to prevent duplicate runtime ownership."
The trigger is the `proxy:` block, **not** the image/name — a user may run
their own traefik/caddy/nginx as an ordinary `services:` entry, which is
project-scoped and stays in the compose.

**The regression:** `build_proxy_service()`
(`src/cli/generator/compose.rs`) synthesizes the proxy as a compose
service stamped `my.stacker.scope: "platform"`, and the config-bundle
deploy path ships that compose **verbatim** → the proxy lands in the
project compose AND is deployed again by the backend role → both bind
80/443/81 → the role's preflight fails `PRECHECK_PORT_CONFLICT rc: 42`
(mis-reported as generic `hcloud... unclassified internal error`, #241).

Why the existing exclusion misses it: `PLATFORM_MANAGED_APP_CODES =
["nginx_proxy_manager","statuspanel"]` is applied only in
`build_project_body()` (app *registration*) over `config.services` — the
synthesized proxy isn't a `config.service`, so it's never filtered. The
config-bundle compose path has no platform filter.

**Correct fix (agreed, not yet implemented):** discriminate by the
`my.stacker.scope == platform` label (already set on synthesized proxies;
user services lack it) — NOT by image name (do not extend
`PLATFORM_MANAGED_APP_CODES` with traefik/caddy: it's name/image-based and
would over-match user services). Piece 1: strip `scope: platform` services
from the compose shipped to the backend on **cloud/server** deploys (keep
them for `--target local`, where no backend role runs). Generalizing to
traefik/caddy is gated on their backend roles + `proxy.type→role-tag`
mapping existing and being verified functional (unconfirmed as of
2026-08-23; roles are in the private `tools/stacks` submodule). Caddy is
also not yet a `ProxyType` variant. Separately, #242 (routing config from
`proxy.domains` never generated) is orthogonal — deploy != route.

### NPM proxy-manager preflight false positive (symptom of the above)

**Bug:** `nginx-proxy-manager` role starts the container, then the preflight
check runs — NPM's own ports (80, 443, 81) show as occupied, failing with
`rc: 42`. This is a self-conflict: the role started the container, then the
preflight sees its ports and blocks.

**Workaround:** Deploy with `proxy: none`, then configure NPM manually:

```yaml
proxy:
  type: none
```

```bash
# After deploy, configure NPM via API
curl -sk -X POST http://<server>:81/api/tokens \
  -H 'Content-Type: application/json' \
  -d '{"identity":"admin@example.com","secret":"changeme"}'
```

### NPM proxy-manager missing volumes

**Bug:** The platform-managed proxy-manager service in generated compose is
missing `/etc/letsencrypt` and data volume mounts, causing restart loops.

**Fix:** Patch the generated compose on the server after deploy:

```bash
# Pull correct image and add volumes
ssh root@<server> "cd /home/trydirect/project && \
  sed -i 's|image: jc21/nginx-proxy-manager:latest|image: trydirect/nginx-proxy-manager:stable|' docker-compose.yml && \
  sed -i '/my.stacker.service: nginx_proxy_manager/a\\    volumes:\\n      - /home/trydirect/nginx_proxy_manager/data:/data\\n      - /etc/letsencrypt:/etc/letsencrypt' docker-compose.yml && \
  docker compose up -d proxy-manager"
```

---

## 11. Deployment Verification Checklist

After a cloud deploy:

```bash
# 1. Check deployment status
stacker status

# 2. Check agent health and containers
stacker agent status

# 3. Open firewall ports if auto-firewall didn't trigger
stacker cloud firewall add --public-ports <port>/tcp

# 4. Verify app is reachable
curl -sf http://<server-ip>:<port>/

# 5. Check container logs for errors
stacker agent logs <app-name>

# 6. Check post_deploy hook ran (if configured)
```

### HTTP status codes

| Code | Meaning |
|---|---|
| 200 | Working |
| 302 | Redirecting (follow with `-L`) |
| 500 | App issue (check logs) |
| 000 | Port not reachable (firewall or container not running) |

---

## 12. Common Failure Patterns

### "Deployment paused — internal error"

Usually a `local-exec provisioner error` in the Install Service's Ansible
playbook. Check the deployment log:

```bash
stacker status
```

Common causes:
- Container failed to start (wrong image, missing env vars)
- Port conflict on host (see pihole port 53)
- Health check timed out
- Network/DNS resolution failure

### "Application Stack: <name>" error

The Install Service failed during the app deployment step. The server is
provisioned but the containers couldn't start. SSH investigation needed.

### "local-exec provisioner error" / generic "paused due to internal error"

stacker collapses the real failure into a generic wrapper string —
`stacker status`/`stacker deployment events` will NOT show the actual
cause. The real error lives only in the backend's Terraform/Ansible
subprocess log (`watchers.py execute_tf()`), which the CLI doesn't
expose. **You cannot diagnose these from stacker alone** — this is a known
observability gap ([stacker#241](https://github.com/trydirect/stacker/issues/241),
generalizing the closed #222). Common real causes hidden behind this
string: a host **port conflict** on the target (e.g. `Bind for
0.0.0.0:5000 failed: port is already allocated` — statuspanel uses 5000),
a container crash on start, or a provider quota error. To actually
diagnose: SSH to the server and read `docker`/journal logs, or get the
raw TF/Ansible log from the backend. Don't just retry blindly — but note
that retrying is often all you *can* do from the CLI until #241 lands.

### SSH key not accessible

New servers provisioned with `--force-new` don't have a local backup SSH key if
the deploy command timed out before the key was saved. Use Vault-backed keys
or check `~/.config/stacker/ssh/` for the key file.

### Cloud deploy: server created but IP never assigned (2026-08-14)

```bash
# Verify server type is available in region
curl -s "https://api.hetzner.cloud/v1/server_types" -H "Authorization: Bearer $HTZ_TOKEN" | jq '.server_types[] | select(.name=="cpx21") | .locations'
```

**Status:** Logged in `BUGS.md`. Needs fix in Stacker Install Service.

### Cloud deploy paused: Hetzner firewall limit exceeded (recurring, 2026-08-19)

Same symptom as above (generic "paused"/"IP not available"), different root
cause — always check `stacker status` before assuming it's a new bug:

```
Error: firewall limit exceeded (resource_limit_exceeded, <id>)
```

The Hetzner test account has accumulated 500+ servers/firewalls from
repeated `stacker deploy --target cloud` runs across this repo's 246
projects and has hit an account-level firewall quota. `stacker servers`
shows the full (long) list. This is an environment/account issue, not a
per-project config bug — a project with a clean `stacker.yml` (verified via
`--target local`) can still fail cloud deploy for this reason.

**Do not delete servers/firewalls to fix this** — servers must never be
deleted via API/CLI/any method (see global rule); this needs sanctioned
cleanup or a quota increase, not agent action. When blocked, fall back to
`--target server` (existing server) to still verify the deploy path, and
note the block in the project's `BUGS.md` referencing this section instead
of re-diagnosing from scratch.

---

## 13. Config Pipeline (Rust Source Map)

| File | Role |
|---|---|---|
| `src/cli/config_parser.rs:246` | `ServiceDefinition` — `name`, `image`, `ports`, `environment`, `volumes`, `depends_on`, `command`, `healthcheck` |
| `src/cli/config_parser.rs:195` | `AppSource` — `app_type`, `path`, `dockerfile`, `image`, `build`, `ports`, `volumes`, `environment`, `command`, `healthcheck` |
| `src/cli/config_parser.rs:270` | `ComposeHealthcheck` — `test`, `interval`, `timeout`, `retries` |
| `src/cli/config_parser.rs:573` | `InstallConfig` — `inputs` map (template variables) |
| `src/cli/config_parser.rs:739` | `ConfigContract` — `services` with `required`, `optional`, `secret` declarations |
| `src/cli/config_parser.rs:1295` | `${VAR_NAME}` substitution — resolves from OS env + `env_file` |
| `src/cli/config_parser.rs:542` | `CloudConfig` struct — `provider`, `region`, `size`, `public_ports` |
| `src/cli/generator/compose.rs:179` | `build_app_service` — constructs `ComposeService` from `AppSource` |
| `src/cli/generator/compose.rs:324` | `render()` — writes docker-compose.yml from `ComposeService` structs |
| `src/cli/compose_service_sync.rs:232` | `service_to_compose_value` — converts `ServiceDefinition` to compose YAML |
| `src/cli/config_bundle.rs:67` | `build_config_bundle` — collects bind-mount files, env_file, creates tar.zst archive |
| `src/cli/config_bundle.rs:224` | `rewrite_compose_references` — rewrites compose volume refs to bundle destinations |
| `src/cli/config_bundle.rs:301` | `rewrite_volumes` — processes each volume mount in compose |
| `src/cli/config_bundle.rs:348` | `parse_bind_mount` — identifies bind mounts (starts with `.`, `/`, `~`, or contains `/`) |
| `src/cli/config_bundle.rs:361` | `collect_reference` — resolves path, collects file, returns destination path (with `./` prefix fix) |
| `src/cli/config_bundle.rs:373` | `collect_file` — canonicalizes, validates, reads file bytes |
| `src/cli/config_bundle.rs:519` | `display_project_path` — strips project root from canonical path |
| `src/cli/stacker_client.rs:3493` | `parse_docker_image` — splits `user/repo:tag` into name + tag |
| `src/cli/stacker_client.rs:3890` | `build_deploy_form` — builds JSON sent to API |
| `src/cli/stacker_client.rs:3826` | `attach_config_bundle_to_deploy_form` — adds `config_files` + `config_bundle` to deploy form |
| `src/forms/project/docker_image.rs:7` | `DockerImage` — struct with `dockerhub_user`, `dockerhub_name`, `dockerhub_image`, `dockerhub_tag`, `dockerhub_password` |
| `src/forms/project/deploy.rs:59` | API `Deploy` form — receives deploy request |
| `src/routes/project/deploy.rs:1235` | `execute_deployment` — orchestrates deploy |
| `src/routes/project/deploy.rs:1277` | `apply_deploy_bundle` — stores `config_files`/`config_bundle` in `project.metadata` |
| `src/console/commands/cli/deploy.rs:3268` | `build_config_bundle` call site — passes `project_dir` or compose parent as `reference_base` |
| `src/forms/firewall.rs:40` | `parse_public_port` — parses "8000" or "53/udp" |

---

## 13.5 Debugging/Verification Workflow — Prefer stacker CLI

When verifying a deploy, exhaust `stacker` subcommands before falling back
to `ssh`/`docker`/`curl`-only investigation — this also stress-tests the
CLI itself, which is the point of this repo:

```bash
stacker status                          # deployment status + log tail
stacker deployment events               # full event log (status can truncate)
stacker agent status                    # container list for the active deployment
stacker agent health                    # per-container CPU/mem + overall health
stacker agent health --deployment <hash> # same, pinned to a specific deployment
stacker logs --service <name> --tail 50  # per-service logs (NOT `stacker logs <name>` — service is a flag)
stacker cloud firewall list --server-id <id>  # confirm auto-firewall actually opened the ports
```

**Known gap:** `stacker agent status` and `stacker agent health` each pick
their own "active deployment" for a project when `--deployment` is
omitted, and can disagree with each other if the project has more than one
deployment (e.g. one to cloud, one to an existing server) — see
[stacker#234](https://github.com/trydirect/stacker/issues/234). Always
pass `--deployment <hash>` explicitly once you have more than one
deployment for the same project; don't trust the auto-selected default.

Only drop to `ssh`/`docker exec` when a stacker command's output is
insufficient (e.g. `stacker status`/`stacker deployment events` truncate
the real Ansible failure — see the port-conflict example in §12) — and
note the gap in the project's `BUGS.md` as a potential missing stacker
feature.

If, after checking this file and `stacker --help`/`stacker <cmd> --help`,
a needed capability genuinely doesn't exist, file a feature request or bug
report at https://github.com/trydirect/stacker/issues (check existing
issues first with `gh issue list --repo trydirect/stacker --search
"<keywords>"` to avoid duplicates).

**Don't trust "this is fixed" claims — re-reproduce, and re-check after
every "just updated."** When told a stacker release/build now includes a
fix for issue N, re-run the original repro steps against the current
build before updating any docs/memory — and if the claim doesn't hold up,
don't assume it's permanently wrong either; some fixes need an actual
backend redeploy, not just a merge/CLI update, so re-test again next time
you're told "just updated."

Case study, 2026-08-19/20, build `0.3.1 (144d1a6)`:
- stacker#219 (`stacker status` omitting `app` from Services) — fixed on
  first check.
- stacker#211 (remote compose referencing undefined network
  `default_network` instead of the real `trydirect_network`) — claimed
  fixed twice, still reproduced both times (confirmed via
  `stacker agent deploy-app <app> --image <img> --force`, verified the
  remote compose file itself was freshly rendered, not cached). Fixed on
  the third check, after an explicit "stacker was just updated."
- stacker#236 (NEW) — confirming #211 immediately surfaced a sibling bug
  in the *same* render path: services with named volumes render fine
  individually, but the top-level `volumes:` block is omitted entirely
  (`service "postgres" refers to undefined volume postgres_data`). When a
  shared renderer/codepath gets fixed for one resource type (networks),
  check sibling resource types (volumes) for the same bug class — that's
  exactly how this was found.

---

## 14. Testing

```bash
# Build
SQLX_OFFLINE=true cargo build

# Run all library tests
cargo test --lib

# Check for warnings
cargo clippy -- -D warnings
```

After changing any `sqlx` query:

```bash
cargo sqlx prepare
```

---

## 15. Deploy command reference

```bash
# Standard cloud deploy (new server)
stacker deploy --target cloud --key=htz-0 --force-new

# Redeploy with updated compose (existing server)
stacker deploy --target cloud --key=htz-0 --force-rebuild

# Redeploy to existing server (reuse locked server)
stacker deploy --target cloud --key=htz-0

# With environment selection (coolify-style)
stacker deploy --target cloud --key=htz-0 --force-new --environment production
```

### ⚠️ `--force-rebuild` on fresh cloud deploys

**Do NOT use `--force-rebuild` with `--force-new` on a fresh cloud deploy.**
This combination causes SSH key installation to fail — the key is saved locally
but never installed on the server. Use `--force-new` alone for new servers, and
`--force-rebuild` only for redeploying to existing servers.

### Dual-target stacker.yml pattern

Keep both `server` and `cloud` sections in `stacker.yml`. The `--target` flag
selects which one to use:

```yaml
deploy:
  target: server          # default target (can be overridden by --target)
  server:
    host: ${EXISTING_SERVER_HOST}
    user: ${EXISTING_SERVER_USER}
    ssh_key: ${BASE_PATH}/stacker-project-test
  cloud:
    provider: hetzner
    region: fsn1
    size: cpx22
    public_ports:
      - "5000"
```

```bash
# Deploy to existing server (uses deploy.server)
stacker deploy --target server

# Deploy to fresh cloud (uses deploy.cloud)
stacker deploy --target cloud --key htz-0 --force-new
```

---

## 16. Hooks — Execution & Safety

`hooks.pre_build`, `hooks.post_deploy`, and `hooks.on_failure` run scripts around
the deploy. Every project in this repo uses `pre_build` to run
`generate-secrets.sh`. Things that bite people:

- **Cleared environment.** Hooks run with only `PATH` and `HOME` set — none of
  your shell's exported vars are visible. Read config from `.env` inside the
  hook, don't assume `$DB_PASSWORD` is in the environment.
- **5-minute hard timeout.** A hook that waits on a slow pull or migration is
  killed at 5 min. Keep hooks fast; move long setup into `app.command:` (§4).
- **Marketplace marker blocks execution.** A leading
  `# @stacker-origin: marketplace` line in a hook script blocks *all* hooks until
  the line is deleted (or you pass `--allow-untrusted-hooks`). If your
  `generate-secrets.sh` silently never runs, check for this line first.
- **Rejected patterns.** Absolute paths, `..` traversal, pipe-to-shell, and
  reverse-shell patterns are rejected before execution. Keep hook paths
  relative: `./scripts/generate-secrets.sh`.
- **CI:** `stacker deploy --no-hooks` skips all hooks. Generate secrets in a
  prior CI step instead.

---

## 17. Secrets: Vault-backed vs `.env`

Two mechanisms, used together:

| | `.env` + `generate-secrets.sh` (§5) | `stacker secrets` (Vault) |
|---|---|---|
| Where it lives | Local file, gitignored | Server-side Vault |
| Best for | Local/dev, single-server | Cloud, shared, rotated secrets |
| Set | Auto-generated by hook | `stacker secrets set KEY --scope service --service <app> --body "<val>"` |
| Push | Read via `env_file:` | `stacker secrets push --service <app> --env production` |

Reserved key prefixes are **rejected** by Vault: `STACKER_`, `DOCKER_`,
`VAULT_`, `AGENT_`. Name app secrets around them (e.g. `APP_DB_PASSWORD`, not
`DOCKER_PASSWORD`).

Whichever you use, the rule from §6 holds: secrets are `${ENV_VAR}` references
resolved at deploy time — never `install.inputs` values, which are stored in the
DB as plaintext stack vars.

---

## 18. Status Panel Agent — Daemon Mode & Pipe Execution

### Architecture overview

The Stacker PIPE system uses two components on the target server:

| Component | Purpose | Mode |
|---|---|---|
| `statuspanel` | Web UI + API on port 5000 | `serve --with-ui` |
| `statuspanel_agent` | Long-polling daemon that receives and executes pipe commands | daemon (`-c /app/config.json`) |

The agent polls the Stacker dashboard API for pending commands (e.g.,
`trigger_pipe`, `pipe_scan`), executes them locally via `docker exec` on
the target server, and reports results back.

### Deployment

Deploy both containers using the Stacker agent API:

```bash
# 1. Register agent (gets AGENT_TOKEN + deployment hash)
curl -X POST "https://stacker.try.direct/api/v1/agent/register" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_code": "<PROJECT_CODE>",
    "project_id": <PROJECT_ID>,
    "deployment_hash": "deployment_<HASH>",
    "deployment_id": <DEPLOYMENT_ID>,
    "server_ip": "<SERVER_IP>",
    "apps": ["directus", "chatwoot"]
  }'

# 2. Create agent config
cat > agent-config.json << 'EOF'
{
  "api_base": "https://stacker.try.direct",
  "agent_token": "<AGENT_TOKEN>",
  "deployment_hash": "deployment_<HASH>",
  "log_file": "/var/log/agent.log",
  "log_level": "info"
}
EOF

# 3. Deploy status panel (UI + daemon)
docker run -d \
  --name statuspanel \
  --restart unless-stopped \
  --network project_app-network \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v agent-config.json:/app/config.json:ro \
  -e DATABASE_URL="..." \
  -p 127.0.0.1:5000:5000 \
  trydirect/status:pipe-agent-fixes \
  --entrypoint /usr/local/bin/status \
  -c /app/config.json

# 4. Deploy agent daemon (separate container, no UI)
docker run -d \
  --name statuspanel_agent \
  --restart unless-stopped \
  --network project_app-network \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  -v agent-config.json:/app/config.json:ro \
  trydirect/status:pipe-agent-fixes \
  --entrypoint /usr/local/bin/status \
  -c /app/config.json
```

**Critical:** The agent must run in daemon mode (`-c /app/config.json`),
**not** `serve --with-ui`. The default Dockerfile entrypoint starts the web
server, which does not poll for commands.

### Network requirements

The agent must be on the **same Docker network** as the project containers
it manages:

```bash
docker network connect project_app-network statuspanel_agent
```

Without this, the agent can resolve container names but cannot reach them
(IPs are not routable across networks).

### Deployment hash

The agent registers with a specific `deployment_hash` (format:
`deployment_<hex>`). This hash is returned by the Stacker API after a
successful deploy. Using the wrong hash causes 403 auth errors.

```bash
# Find the deployment hash
curl -s "https://stacker.try.direct/api/v1/project/<ID>/deployments" \
  -H "Authorization: Bearer $TOKEN" | jq '.[0].deployment_hash'
```

### Pipe trigger flow

```
CLI "stacker pipe trigger"
  → Dashboard API enqueues trigger_pipe command
  → Agent polls /api/v1/agent/commands/wait/{deployment_hash}
  → Agent receives command JSON
  → Agent executes via docker exec on target container
  → Agent reports result back to API
```

### Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Agent 403 auth error | Wrong deployment hash | Re-register with correct `deployment_hash` |
| Agent running in serve mode | Dockerfile entrypoint | Override with `--entrypoint /usr/local/bin/status -c /app/config.json` |
| Pipe scan timeout | Agent not on same network | `docker network connect project_app-network statuspanel_agent` |
| Pipe trigger timeout | Agent not in daemon mode | Ensure `-c /app/config.json` flag, not `serve --with-ui` |
| `curl: not found` in pipe trigger | Target container missing curl | Install curl in target container or use different HTTP client |

### Verification

```bash
# Check agent mode
docker logs statuspanel_agent --tail 20
# Should show: mode="Status Panel Daemon", polling for commands

# Test pipe scan
stacker pipe scan <project> --server <IP>
# Should return: "success", resolved container, endpoints: [...]

# Test pipe trigger
stacker pipe trigger <project> --server <IP> --pipe <PIPE_NAME>
# Should execute command (may fail at curl if container lacks it, but mechanism works)
```
