# awesome-selfhosted-stacker

> **266 self-hostable apps, each deployable with a single `stacker.yml`.**
> Deploy to your laptop, your own server, or the cloud with one command -
> database setup, health checks, secrets, and remote monitoring included.

<p>
  <img alt="Projects" src="https://img.shields.io/badge/projects-266-blue">
  <img alt="Tested" src="https://img.shields.io/badge/tested%20%26%20verified-172-brightgreen">
  <img alt="Targets" src="https://img.shields.io/badge/deploy-local%20%7C%20server%20%7C%20cloud-orange">
  <img alt="Powered by" src="https://img.shields.io/badge/powered%20by-Stacker-8A2BE2">
</p>

Eevery entry here is a **ready-to-run deployment**: 
Pick a directory, generate secrets, and `stacker deploy`. Same layout, same commands.

```bash
cd stacker-projects/umami         # pick any project, for instance umami
./scripts/generate-secrets.sh     # generate .env from .env.example
stacker deploy                    # → running locally in minutes
```

### Quick deploy to cloud and remote control

```bash
export HETZNER_API_TOKEN=your_token
stacker deploy --target cloud --force-rebuild
```

<p>
  <a href="https://github.com/trydirect/stacker"><img alt="Install Stacker" src="https://img.shields.io/badge/install-Stacker-8A2BE2?style=for-the-badge"></a>
  <a href="https://cloud.hetzner.com"><img alt="Hetzner Cloud" src="https://img.shields.io/badge/deploy%20to-Hetzner-d50c2d?style=for-the-badge"></a>
  <a href="https://github.com/trydirect/stacker#quick-start"><img alt="Quick Start" src="https://img.shields.io/badge/quick-start-2ea44f?style=for-the-badge"></a>
</p>

## Contents

- [Quick Start](#quick-start)
- [Deploy in 30 Seconds](#deploy-in-30-seconds)
- [Deployment Targets](#deployment-targets)
- [PIPE — Connect Apps Together](#pipe--connect-apps-together)
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

## Deploy in 30 Seconds

```bash
# 1. Pick a project
cd plausible

# 2. Generate secrets
./scripts/generate-secrets.sh

# 3. Deploy to cloud
stacker deploy --target cloud --force-rebuild
```

![Stacker deploy](gifs/stacker-plausible.gif)
![Stacker status](gifs/stacker-status.gif)
## Deployment Targets

### Local

Best for development and testing on your own machine.

```bash
stacker deploy
```

### Own Server

Deploy to a Linux server you control (Ubuntu 24.04+/Debian 12+, 2 GB+ RAM,
20 GB+ disk, key-based SSH, Docker installed).

```bash
stacker config setup server --ip <IP> --user root --key ~/.ssh/id_ed25519
stacker deploy --target server --force-rebuild
```

What happens: Stacker uploads the config bundle, generates
`docker-compose.yml` from `stacker.yml` under `.stacker/` on the server, runs
`docker compose up -d`, waits for health checks, then runs post-deploy hooks.

When the Stacker API is unreachable (DNS or auth issues), deploy manually:

```bash
scp .stacker/docker-compose.yml .env root@<IP>:/home/trydirect/project/
ssh root@<IP> "docker compose -f /home/trydirect/project/docker-compose.yml -p project up -d"
```

### Cloud (Hetzner and others)

Fully automated provisioning. Requires a provider account, an API token, and an
SSH key registered with the provider.

```bash
export HETZNER_API_TOKEN=your_token_here

# First deploy — creates a new server (5-10 minutes)
stacker deploy --target cloud --force-new

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
| `cpx42` | 4    | 8 GB  | ~50 EUR   | AI stacks                      |

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

## Reverse Proxy Support

Stacker supports multiple reverse proxy types for automatic HTTPS and domain routing.
Configure in `stacker.yml`:

```yaml
proxy:
  type: traefik         # or: caddy, nginx-proxy-manager, nginx, none
  auto_detect: false
  domains:
    - domain: app.example.com
      ssl: off          # off | auto | manual
      upstream: app:3000
```

### Supported proxy types

| Type | Image | Config | Auto-HTTPS | Notes |
|------|-------|--------|------------|-------|
| `traefik` | traefik:latest | Docker labels | ✅ (Let's Encrypt) | Default for cloud deploys |
| `caddy` | caddy:2-alpine | Caddyfile | ✅ (automatic) | Simple config, zero-touch TLS |
| `nginx-proxy-manager` | jc21/nginx-proxy-manager | Web UI | ✅ (Let's Encrypt) | GUI-based management |
| `nginx` | nginx:alpine | nginx.conf | ❌ | Manual config |
| `none` | — | — | — | No proxy (direct port access) |

### Tested proxy deployments

| Stack | Proxy | Server | Status |
|-------|-------|--------|--------|
| bookstack | traefik | 138.199.238.202 | ✅ agent online |
| ntfy | caddy | 188.245.97.117 | ✅ agent online |
| onetimesecret | caddy | 138.199.238.202 | ✅ agent online |

### Cloud firewall

When deploying to cloud, `public_ports` opens the provider firewall. Without it,
only SSH (22) is open — the #1 cause of "app unreachable after deploy":

```yaml
deploy:
  cloud:
    public_ports:
      - "80"
      - "443"
```

Fix without redeploying:
```bash
stacker cloud firewall add --public-ports 8080/tcp
```

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

### Stacker secrets CLI

Manage secrets locally or remotely via the Stacker CLI:

**Local mode** (reads/writes `.env`):

```bash
stacker secrets list                    # list all secrets in .env
stacker secrets validate                # check all ${VAR} refs are set
stacker secrets set DB_PASSWORD=secret  # set a value in .env
stacker secrets get DB_PASSWORD         # read a value
```

**Remote mode** (Vault-backed, requires deployed project):

```bash
stacker secrets set KEY --scope service --service my-app --body "value"
stacker secrets push --service my-app --env production
stacker secrets list --scope service --service my-app
```

Remote secrets are stored in Vault and layered on top of local `.env` values at
deploy time. Use for production credentials that shouldn't be in files.

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
stacker deploy --target server --force-rebuild
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

**PIPE commands**

```bash
stacker pipe scan                  # discover container endpoints
stacker pipe create <src> <tgt>    # create a data pipe
stacker pipe list                  # list pipe instances
stacker pipe activate <id>         # start a pipe
stacker pipe deactivate <id>       # pause a pipe
stacker pipe trigger <id>          # one-shot execution
stacker pipe history <id>          # view execution log
```


---
## PIPE — Connect Apps Together

Stacker PIPE lets you connect applications on the same server so data flows
automatically between them. Pipes are created at runtime via the CLI — no
stacker.yml changes needed.

**Basic workflow:**

```bash
# 1. Deploy two apps on the same server (one at a time)
stacker deploy --target server --force-rebuild

# 2. Discover available endpoints from running containers
stacker pipe scan

# 3. Create a pipe between source and target
stacker pipe create <source-app> <target-app>

# 3b. Create a pipe with manual endpoints (no discovery)
stacker pipe create <source> <target> \
  --source-endpoint "METHOD /path" \
  --target-endpoint "METHOD /path" \
  --source-fields field1,field2 \
  --target-fields field1,field2 \
  --name "my-pipe"

# 4. Activate the pipe (use --trigger manual for one-shot testing)
stacker pipe activate <pipe-id> --trigger manual

# 5. Trigger a one-shot test
stacker pipe trigger <pipe-id> --data '{"key":"value"}'
```

**Trigger types:**

| Type | Behavior | Use Case |
|------|----------|---------|
| webhook | Fires instantly when data arrives | Real-time notifications |
| poll | Checks for new data every N seconds | Periodic syncs, batch jobs |
| manual | Only runs on explicit `pipe trigger` | Testing, one-off transfers |

**Built-in adapters:** SMTP (target), IMAP/POP3 (source), WebhookBridge,
HttpEndpoint, HtmlForm.

**Example: Contact form → Telegram**

```bash
stacker pipe scan --app website
stacker pipe create website telegram --name "contact-to-telegram"
stacker pipe activate <telegram-pipe-id>
```

See the PIPE HOWTO at `docs/pipe-howto.md` for a complete walkthrough.

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
docker compose ps                  # check the Status column
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

### Tested and verified 

Deployed and confirmed working on a clean Ubuntu 26.04 server via the Stacker
server target. Start here for production.

[Project Index](stacker-projects/INDEX.md)

### New templates (config-validated 2026-10-15)

| Project             | Type             | Port  | Proxy      | Image Fix / Notes |
|---------------------|------------------|-------|------------|--------------------|
| Agent Zero          | AI agent         | 50080 | —          | autonomous agent; generated auth password |
| Archon              | AI assistant     | 3000  | —          | coleam00 stack; needs Claude/OpenAI key at first run |
| Bolt.diy            | AI codegen       | 5173  | —          | stackblitz-labs; 9 LLM providers via env |
| Docling Serve       | Doc AI           | 5001  | —          | IBM doc→markdown/chunks API; API-key auth |
| Evolution API       | WhatsApp API     | 8080  | —          | + postgres + redis; n8n-agency backend |
| kotaemon            | RAG chat         | 7860  | —          | ⚠ open RCE #844 / IDOR #846 — self-host only, never expose publicly |
| Langchain-Chatchat  | AI RAG           | 8501  | —          | stale 2024 images; FAISS + xinference |
| LightRAG            | AI RAG           | 9621  | —          | + postgres + qdrant; no auth by default (upstream) |
| Local AI Packaged   | AI stack         | 8001  | caddy      | full 28-service upstream stack; deployed (#1363) + baked; Quick Deploy in its README |
| LocalAGI            | AI agent         | 8080  | —          | + LocalAI (CPU) + localrecall postgres |
| Mautic              | Marketing        | 8080  | —          | web+worker+cron + mysql; first-run wizard |
| Open Notebook       | Notes            | 8502  | —          | + SurrealDB; default root:root replaced; API on 5055 |
| OpenAgent           | AI knowledge     | 14000 | —          | ex-Casibase; + mysql |
| Paperless GPT       | Doc AI           | 8080  | —          | + paperless-ngx + postgres + redis; LLM labels |
| PipeShub            | AI knowledge     | 3000  | —          | slim: mongo + redis + qdrant + neo4j |
| Scriberr            | Transcription    | 8080  | —          | WhisperX; heavy first boot (model download) |
| Self-hosted AI Kit  | AI stack         | 5678  | —          | official n8n starter: n8n + postgres + ollama + qdrant |
| Speaches            | Speech API       | 8000  | —          | OpenAI-compatible STT/TTS; API-key auth |
| Strata              | AI inference     | 8080  | —          | CUDA build from source; needs stacker gpus support (hand-written compose) |
| Vane                | AI search        | 3000  | —          | Perplexica successor; bundled SearXNG |
| WAHA                | WhatsApp API     | 3000  | —          | WhatsApp HTTP API; sessions volume |



---

## Contributing

Contributions are welcome — **one app per pull request** keeps reviews fast.

**Add a new app:**

1. Create a directory named after the app (lowercase): `mkdir my-app && cd my-app`
2. Add the four standard files:

   ```
   my-app/
     stacker.yml               # deployment config (required)
     .env.example              # public config + empty secret placeholders (required)
     scripts/generate-secrets.sh   # fills .env from .env.example (required)
     README.md                 # 3–5 lines: what it is, default port, any gotchas
   ```

3. Validate before opening the PR:

   ```bash
   stacker config validate
   ./scripts/generate-secrets.sh
   stacker deploy               # confirm it comes up locally
   ```

4. Add a row to the [Project Catalog](#project-catalog) with the correct status
   badge (see legend below).

**Please do:** pin image tags to a specific version (avoid `:latest` — see
[Known image issues](#known-image-issues)); bind database ports to `127.0.0.1`;
keep real secrets out of the PR (only `.env.example` is committed).

**Please don't:** vendor the upstream app's full source tree — this repo ships
**deployment configs**, not application code. A `stacker.yml` that references the
official image is the whole point.

**Status badges** used in the catalog:

| Badge | Meaning |
|-------|---------|
| ✅ | Tested & verified on a real server |
| 🧪 | Configured, not yet re-deployed/verified |
| ⚠️ | Works with a documented workaround (see notes) |

---

## Resources

| Resource           | Link                                                    |
|--------------------|---------------------------------------------------------|
| Stacker            | https://github.com/trydirect/stacker                    |
| Stacker CLI docs   | https://github.com/trydirect/stacker/blob/main/docs/    |
| awesome-selfhosted | https://github.com/awesome-selfhosted/awesome-selfhosted |
| Docker Hub         | https://hub.docker.com                                   |
| Hetzner Docs       | https://docs.hetzner.cloud                               |
| Jitsi Docker guide | https://jitsi.github.io/handbook/docs/devops-guide/devops-guide-docker/ |
| Zitadel compose    | https://zitadel.com/docs/self-hosting/deploy/compose     |

Last updated: 2026-10-11 — 266 projects configured, 172 tested and verified on
Ubuntu 26.04. Proxy support: traefik, caddy, nginx-proxy-manager.

---

<p align="center">
  <sub>⭐ Star this repo if it saved you a weekend of Docker Compose wrangling.</sub><br>
  <sub>Built with <a href="https://github.com/trydirect/stacker">Stacker</a> · Contributions welcome — one app per PR.</sub>
</p>
