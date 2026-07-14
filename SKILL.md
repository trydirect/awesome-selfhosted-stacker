# Stacker Deploy Pipeline Knowledge

## Overview

Stacker deploys containerised apps to cloud (Hetzner) via a multi-step pipeline:

```
stacker.yml → CLI → Stacker API → MQ → Install Service (Terraform + Ansible) → Cloud Server
```

This document captures known issues, fixes, and best practices discovered during
real-world deployments.

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
  sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=$(openssl rand -hex 16)/" .env
fi
# ... repeat for each secret
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

---

## 10. Port Conflict Validation

Stacker validates that two services don't bind the same host port. This
validation is now protocol-aware: `8053/tcp` and `8053/udp` are treated as
different ports.

The fix is in `extract_host_port_from_string` (`deploy.rs:1626`): the protocol
suffix (e.g., `/tcp`, `/udp`) is now included in the extracted host port,
preventing false conflicts when the same host port is used for both protocols.

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

### SSH key not accessible

New servers provisioned with `--force-new` don't have a local backup SSH key if
the deploy command timed out before the key was saved. Use Vault-backed keys
or check `~/.config/stacker/ssh/` for the key file.

---

## 13. Config Pipeline (Rust Source Map)

| File | Role |
|---|---|
| `src/cli/config_parser.rs:246` | `ServiceDefinition` — `name`, `image`, `ports`, `environment`, `volumes`, `depends_on`, `command`, `healthcheck` |
| `src/cli/config_parser.rs:195` | `AppSource` — `app_type`, `path`, `dockerfile`, `image`, `build`, `ports`, `volumes`, `environment`, `command`, `healthcheck` |
| `src/cli/config_parser.rs:270` | `ComposeHealthcheck` — `test`, `interval`, `timeout`, `retries` |
| `src/cli/config_parser.rs:573` | `InstallConfig` — `inputs` map (template variables) |
| `src/cli/config_parser.rs:739` | `ConfigContract` — `services` with `required`, `optional`, `secret` declarations |
| `src/cli/config_parser.rs:1295` | `${VAR_NAME}` substitution — resolves from OS env + `env_file` |
| `src/cli/config_parser.rs:542` | `CloudConfig` struct — `provider`, `region`, `size`, `public_ports` |
| `src/cli/generator/compose.rs:179` | `build_app_service` — constructs `ComposeService` from `AppSource` (now includes `command`/`healthcheck`) |
| `src/cli/generator/compose.rs:324` | `render()` — writes docker-compose.yml from `ComposeService` structs |
| `src/cli/compose_service_sync.rs:232` | `service_to_compose_value` — converts `ServiceDefinition` to compose YAML |
| `src/cli/config_bundle.rs:67` | `build_config_bundle` — rewrites compose references, collects files, creates tar.zst bundle |
| `src/cli/config_bundle.rs:283` | `rewrite_volumes` — processes volume mounts (**NB: skips advanced YAML mapping syntax**) |
| `src/cli/stacker_client.rs:3493` | `parse_docker_image` — splits `user/repo:tag` into name + tag |
| `src/cli/stacker_client.rs:3890` | `build_deploy_form` — builds JSON sent to API |
| `src/forms/project/docker_image.rs:7` | `DockerImage` — struct with `dockerhub_user`, `dockerhub_name`, `dockerhub_image`, `dockerhub_tag`, `dockerhub_password` |
| `src/forms/project/deploy.rs:59` | API `Deploy` form — receives deploy request |
| `src/routes/project/deploy.rs:1235` | `execute_deployment` — orchestrates deploy |
| `src/forms/firewall.rs:40` | `parse_public_port` — parses "8000" or "53/udp" |

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

# Redeploy with updated compose
stacker deploy --target cloud --key=htz-0 --force-new --force-rebuild

# Redeploy to existing server
stacker deploy --target cloud --key=htz-0 --force-rebuild

# With environment selection (coolify-style)
stacker deploy --target cloud --key=htz-0 --force-new --environment production
```
