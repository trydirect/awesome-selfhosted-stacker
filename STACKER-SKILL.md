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

## 2. Install Service Image Override Bug

### Symptom

Postgres containers restart-loop with:

```
there appears to be PostgreSQL data in:
  /var/lib/postgresql/data (unused mount/volume)
This is usually the result of upgrading the Docker image...
```

### Root cause

The Install Service (`trydirect/install-service`) Ansible roles replace
user-configured image tags with `latest` defaults:

| User config | Server's compose |
|---|---|
| `postgres:16-alpine` | `postgres:latest` |
| `clickhouse/clickhouse-server:24.12-alpine` | `clickhouse/clickhouse-server:latest` |

Environment variables and custom volume mounts (init SQL scripts) are also
silently dropped.

### Impact

Every project using postgres on cloud deploy is affected (plausible, umami,
ghost, outline, supabase, etc.).

### Temporary workaround

SSH into the server and patch the compose:

```bash
sed -i 's|image: postgres:latest|image: postgres:16-alpine|' \
  /home/trydirect/project/docker-compose.yml
docker compose -f /home/trydirect/project/docker-compose.yml down -v
docker compose -f /home/trydirect/project/docker-compose.yml up -d
```

### Permanent fix

In the Install Service's Ansible roles: never override user-provided image tags.
If the user specified `postgres:16-alpine`, keep `postgres:16-alpine`.

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
`manage.py migrate`), the `post_deploy` hook can run the command. But it runs
**locally** on the CLI machine — it needs SSH or `stacker agent exec` to reach
the remote server.

---

## 5. Known Project-Specific Issues

| Project | Issue | Fix |
|---|---|---|
| **pihole** | Port 53 taken by systemd-resolved | Use `8053:53/udp` + `8053:53/tcp` |
| **coolify** | Laravel `APP_KEY` missing | Add `APP_KEY` env var |
| **umami** | Old postgres data dir | Use `postgres:15-alpine` + fresh volume |
| **plausible** | DB not auto-created | Add `POSTGRES_DB: plausible` + ClickHouse init SQL |
| **supabase** | 10+ services, complex | Install Service times out |
| **dify** | `orchestrator: remote` | Uses marketplace deploy path, not standard CLI |

---

## 6. Port Conflict Validation

Stacker validates that two services don't bind the same host port. This
validation is now protocol-aware: `8053/tcp` and `8053/udp` are treated as
different ports.

The fix is in `extract_host_port_from_string` (`deploy.rs:1626`): the protocol
suffix (e.g., `/tcp`, `/udp`) is now included in the extracted host port,
preventing false conflicts when the same host port is used for both protocols.

---

## 7. Deployment Verification Checklist

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

## 8. Common Failure Patterns

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

## 9. Config Pipeline (Rust Source Map)

| File | Role |
|---|---|
| `src/cli/config_parser.rs:542` | `CloudConfig` struct — `provider`, `region`, `size`, `public_ports` |
| `src/cli/stacker_client.rs:3890` | `build_deploy_form` — builds JSON sent to API |
| `src/forms/project/deploy.rs:59` | API `Deploy` form — receives deploy request |
| `src/routes/project/deploy.rs:1235` | `execute_deployment` — orchestrates deploy |
| `src/console/commands/mq/listener.rs:94` | `extract_public_ports` — reads ports from metadata |
| `src/console/commands/mq/listener.rs:216` | `configure_public_firewall_for_deployment` — auto-firewall |
| `src/forms/cloud_firewall.rs:287` | `publish_public_firewall_rules` — publishes firewall message to MQ |
| `src/routes/server/cloud_firewall.rs:21` | Manual firewall endpoint `POST /{id}/cloud-firewall` |
| `src/forms/firewall.rs:40` | `parse_public_port` — parses "8000" or "53/udp" |
| `src/forms/cloud_firewall.rs:158` | `CloudFirewallOperationMessage` — MQ message format |
| `src/connectors/install_service/client.rs:183` | `configure_cloud_firewall` — publishes to `install.firewall.htz.v1` |

---

## 10. Testing

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

## 11. Deploy command reference

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
