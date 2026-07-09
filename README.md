# Stacker Self-Hosted Projects

A collection of self-hostable applications, each with a complete `stacker.yml`:
database setup, health checks, and deployment support for local, own-server, and
cloud targets.

## Contents

- [Quick Start](#quick-start)
- [Deployment Targets](#deployment-targets)
- [Remote Monitoring Without SSH](#remote-monitoring-without-ssh)
- [Secret Management](#secret-management)
- [Common Commands](#common-commands)
- [Customization](#customization)
- [Security Checklist](#security-checklist)
- [Troubleshooting](#troubleshooting)
- [Project Catalog](#project-catalog)
- [Resources](#resources)

---

## Quick Start

```bash
cd umami                 # pick any project directory
./scripts/generate-secrets.sh   # create .env from .env.example
stacker deploy           # deploy locally
```

Then open `http://localhost:PORT` (the port is defined in the project's
`stacker.yml`).

If the CLI is missing, see the installation guide:
https://github.com/trydirect/stacker

**Prerequisites (local):** Docker, Docker Compose, and the Stacker CLI.

---

## Deployment Targets

### Local

Best for development and testing on your own machine.

```bash
stacker deploy
```

### Own Server

Deploy to a Linux server you control (Ubuntu 20.04+/Debian 11+, 2 GB+ RAM,
20 GB+ disk, key-based SSH, Docker installed).

```bash
stacker deploy --target server \
  --server-host example.com \
  --server-user root \
  --server-port 22 \
  --server-ssh-key ~/.ssh/id_ed25519
```

What happens: Stacker uploads the config bundle, generates
`docker-compose.yml` from `stacker.yml` under `.stacker/` on the server, runs
`docker-compose up -d`, waits for health checks, then runs post-deploy hooks.

### Cloud (Hetzner and others)

Fully automated provisioning. Requires a provider account, an API token, and an
SSH key registered with the provider.

```bash
export HETZNER_API_TOKEN=your_token_here

# First deploy — creates a new server (5-10 minutes)
stacker deploy --target cloud --force-rebuild --force-new

stacker status           # get the server IP, then point DNS at it

# Later deploys — reuse the same server (omit --force-new)
stacker deploy --target cloud --force-rebuild
```

Cloud settings live in `stacker.yml`:

```yaml
deploy:
  target: cloud
  cloud:
    provider: hetzner         # or: digitalocean, aws, linode, vultr
    region: fsn1              # Frankfurt (nbg1, hel1, ash, hil, sjc, sin, ...)
    size: cpx22              # 2 vCPU / 4 GB RAM
    ssh_key: ~/.ssh/id_ed25519
    public_ports:            # REQUIRED — without it only SSH (22) is open
      - "80"
      - "443"
```

`public_ports` opens the provider firewall. Forgetting it is the most common
cause of "app unreachable after deploy." You can also add ports afterwards:

```bash
stacker cloud firewall add --public-ports 8080/tcp
```

Hetzner server sizes:

| Size    | vCPU | RAM   | Price     | Best for                       |
|---------|------|-------|-----------|--------------------------------|
| `cpx12` | 1    | 2 GB  | ~11.49 EUR| Small apps, testing            |
| `cx23`  | 2    | 4 GB  | ~5.49 EUR | Most apps                      |
| `cpx32` | 4    | 8 GB  | ~35 EUR   | Heavy / multiple apps          |

---

## Remote Monitoring Without SSH

Enable the status panel in `stacker.yml` so the Stacker agent can serve logs and
health from remote servers directly through the CLI — no SSH required:

```yaml
monitoring:
  status_panel: true
  healthcheck:
    endpoint: /health
    interval: 30s
```

With `status_panel: true`, the `stacker agent` commands read directly from your
remote deployment:

```bash
stacker agent health                     # service health at a glance
stacker agent logs app-name --lines 200  # tail logs remotely
stacker agent status                      # server + container status
```

This is the recommended way to inspect running services. Reserve manual
`ssh root@server` access for cases the agent cannot cover.

---

## Secret Management

Each project ships a generator that fills `.env` from `.env.example`:

```bash
cd project-name
./scripts/generate-secrets.sh   # run once
```

Generated values by naming convention:

| Variable pattern | Method                    | Length    | Used for               |
|------------------|---------------------------|-----------|------------------------|
| `*_PASSWORD`     | `openssl rand -hex 16`    | 32 chars  | DB / service passwords |
| `*_SECRET*`      | `openssl rand -hex 32`    | 64 chars  | App encryption keys    |
| `*_TOKEN`        | `openssl rand -base64 32` | 43 chars  | Auth tokens            |
| `*_KEY`          | `openssl rand -hex 32`    | 64 chars  | Encryption keys        |
| `*_BASE`         | `openssl rand -hex 64`    | 128 chars | Framework keys         |

Edit `.env` by hand for domains and app-specific values. Never commit `.env`
(the included `.gitignore` protects it).

---

## Common Commands

**Configuration**

```bash
stacker config validate            # check stacker.yml
stacker config show --resolved     # show config with variables resolved
```

**Deployment**

```bash
stacker deploy                     # local
stacker deploy --target server --server-host example.com
stacker deploy --target cloud --force-rebuild
stacker deploy --dry-run           # preview changes
stacker deploy --no-hooks          # skip hooks (CI)
```

**Monitoring** (works remotely with `monitoring.status_panel: true`)

```bash
stacker status                     # deployment status
stacker agent health               # agent + service health
stacker agent logs app_name --lines 100
```

**Docker (local / on-server)**

```bash
docker-compose ps                  # list containers
docker-compose logs -f app_name    # live logs
docker-compose restart db          # restart a service
docker-compose down                # stop (add -v to also delete data)
docker exec -it app_name sh        # shell into a container
```

---

## Customization

Edit the project's `stacker.yml`.

**Switch database to PostgreSQL**

```yaml
services:
  - name: db
    image: postgres:16-alpine
    environment:
      POSTGRES_PASSWORD: "${DB_PASSWORD}"
      POSTGRES_DB: myapp
```

**Change the exposed port**

```yaml
app:
  ports:
    - "8080:8080"   # host:container
```

**Add environment variables**

```yaml
app:
  environment:
    CUSTOM_VAR: "static_value"
    DYNAMIC_VAR: "${FROM_ENV_FILE}"
```

**Add a Redis cache (bound to localhost)**

```yaml
services:
  - name: redis
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redis_data:/data
```

---

## Security Checklist

Before deploying:

- [ ] Generated secrets with `./scripts/generate-secrets.sh`
- [ ] Updated domains and admin passwords in `.env`
- [ ] Confirmed `.env` and `.stacker/` are never committed
- [ ] Cloud only: `public_ports` limited to the ports you actually need
- [ ] Configured SSL/TLS and database backups
- [ ] Health checks enabled (included by default)

Never commit: `.env`, `.env.local`, `.stacker/`.

---

## Troubleshooting

**Container won't start**

```bash
docker logs container_name
docker inspect container_name | grep -A 20 "Env"
```

**Port already in use**

```bash
lsof -i :8080          # find the process, then kill it
# or change the port in stacker.yml
```

**Database connection failed**

```bash
docker-compose ps                    # check the Status column
docker exec db_container pg_isready
```

**Can't reach the app**

```bash
# Local: confirm the port is listening
netstat -tulpn | grep 8080

# Cloud: open the firewall port
stacker cloud firewall add --public-ports 8080/tcp
stacker cloud firewall list
```

**High memory usage** — inspect with `docker stats`, then add limits:

```yaml
services:
  app:
    mem_limit: 512m
    memswap_limit: 1g
```

---

## Project Catalog

Each project follows the same layout:

```
project-name/
  .env.example              # template (committed)
  .env                      # secrets (gitignored)
  stacker.yml               # deployment config
  scripts/generate-secrets.sh
```

### Tested and verified (10)

Deployed and confirmed working (2026-07-07). Start here for production.

| Project    | Type         |
|------------|--------------|
| ArchiveBox | Web archive  |
| AstrBot    | AI chatbot   |
| Floci      | Deployment   |
| Ghost      | Blogging     |
| Outline    | Team wiki    |
| Plausible  | Analytics    |
| ROMM       | ROM manager  |
| StackDog   | DevOps tool  |
| Umami      | Analytics    |
| UptimeKuma | Monitoring   |

### Configured, not yet verified (53)

Use these for testing; report results on GitHub to help verify them.

- **Analytics & BI:** Aptabase, Countly, d8a, Daily Stars Explorer, Druid, GoAccess, GoatCounter, HitKeep, Matomo, Metabase, Offen, Plausible, PostHog, Redash, Rybbit, Superset
- **Collaboration:** Rocket.Chat, Synapse, Zulip, Jitsi Meet, Mastodon, Lemmy, Discourse, Postiz App, Socioboard
- **Content & CMS:** WordPress, Strapi, Nextcloud, ComfyUI, Dify
- **Documents:** Paperless-ngx, Wallabag, linkding, ArchivesSpace, Mail Archiver, OpenArchiver
- **Developer tools:** Activepieces, Gitea, Coolify, HermesAgent, insforge, Middleware
- **Media & storage:** Jellyfin, Bitwarden, Bitmagnet, Ganymede, Pi-hole, RustFS, S4Core
- **Other:** Open-WebUI, Statistics for Strava, Supabase, SwarmUI, Vaultwarden

---

## Resources

| Resource           | Link                                                    |
|--------------------|---------------------------------------------------------|
| Stacker            | https://github.com/trydirect/stacker                    |
| awesome-selfhosted | https://github.com/awesome-selfhosted/awesome-selfhosted |
| Docker Hub         | https://hub.docker.com                                   |
| Hetzner Docs       | https://docs.hetzner.cloud                               |

Last updated: 2026-07-08 — 10/63 projects tested, 53 awaiting verification.
