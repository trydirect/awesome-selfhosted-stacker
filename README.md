# awesome-selfhosted-stacker

> **244 self-hostable apps, each deployable with a single `stacker.yml`.**
> Deploy to your laptop, your own server, or the cloud with one command —
> database setup, health checks, secrets, and remote monitoring included.

<p>
  <img alt="Projects" src="https://img.shields.io/badge/projects-244-blue">
  <img alt="Tested" src="https://img.shields.io/badge/tested%20%26%20verified-164-brightgreen">
  <img alt="Targets" src="https://img.shields.io/badge/deploy-local%20%7C%20server%20%7C%20cloud-orange">
  <img alt="Powered by" src="https://img.shields.io/badge/powered%20by-Stacker-8A2BE2">
</p>

Unlike a typical [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted)
list of links, every entry here is a **ready-to-run deployment**: pick a
directory, generate secrets, and `stacker deploy`. Same layout, same commands,
every app — from analytics and CMS to chat, password managers, and AI tools.

```bash
cd umami                          # pick any project
./scripts/generate-secrets.sh     # generate .env from .env.example
stacker deploy                    # → running locally in minutes
```

### Quick deploy to cloud

```bash
export HETZNER_API_TOKEN=your_token
cd umami
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

---

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

**Docker (local / on-server)**

```bash
docker compose ps                  # list containers
docker compose logs -f app_name    # live logs
docker compose restart db          # restart a service
docker compose down                # stop (add -v to also delete data)
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

### Tested and verified (110)

Deployed and confirmed working on a clean Ubuntu 26.04 server via the Stacker
server target. Start here for production.

| Project             | Type             | Port  | Proxy      | Image Fix / Notes |
|---------------------|------------------|-------|------------|--------------------|
| Activepieces        | Automation       | 8080  | —          | Zapier alternative |
| AnythingLLM         | AI chat          | 3001  | caddy      | LLM chat with vector DB |
| AnyCable           | Websocket        | 8080  | caddy      | Real-time websocket server |
| Apache Airflow      | Automation       | 8080  | caddy      | Workflow automation + postgres |
| Appsmith            | Low-code         | 80    | —          | Internal tool builder |
| Aptabase            | Analytics        | 3000  | caddy      | + postgres + clickhouse |
| Bitmagnet           | BitTorrent       | 3333  | —          | + postgres |
| Bitwarden          | Password mgr     | 80    | —          | vaultwarden + postgres |
| BookStack           | Documentation    | 6875  | traefik    | Wiki + MariaDB |
| Chatwoot           | Support          | 3000  | caddy      | Customer support + postgres + redis |
| Centrifugo         | Websocket        | 8000  | caddy      | Real-time messaging |
| ClickHouse         | Database         | 8123  | caddy      | Column-oriented OLAP database |
| CyberChef           | Data tools       | 8000  | —          | container listens on 8080 |
| Cronicle           | Scheduler        | 3012  | caddy      | Job scheduler |
| Dashy               | Dashboard        | 8082  | —          | container listens on 8080, not 80 |
| d8a                 | Analytics        | 3000  | —          | |
| Dagu               | Automation       | 8080  | caddy      | Workflow automation |
| Daily Stars Explorer| Astronomy        | 8080  | —          | |
| Directus            | Headless CMS     | 8055  | —          | REST + GraphQL API |
| Discourse           | Forum            | 80    | —          | needs pgvector/pgvector instead of plain postgres |
| Docmost             | Wiki             | 3000  | —          | needs Redis service |
| Druid               | Analytics        | 8888  | —          | pinned apache/druid:31.0.0; removed broken druid_extensions_loadList env var |
| Duplicati           | Backup           | 8200  | caddy      | Encrypted backup to cloud/local |
| FileBrowser         | File manager     | 8080  | —          | |
| Focalboard         | Kanban           | 8000  | caddy      | Kanban board + postgres |
| Element            | Matrix chat      | 8080  | caddy      | Matrix chat client |
| Floci               | Local cloud      | 4500  | —          | TLS disabled; FLOCI_BASE_URL must match external IP |
| Ganymede           | Video archive    | 4000  | —          | |
| Gitea              | Git hosting      | 3000  | —          | |
| Gitness            | Git hosting      | 3000  | —          | needs GITNESS_PRINCIPAL_ADMIN_EMAIL |
| Ghost              | Blogging         | 2368  | —          | |
| Glances            | System monitor   | 61208 | —          | |
| Gotify             | Notifications    | 8080  | —          | |
| GoatCounter        | Analytics        | 8080  | caddy      | single container, no secrets |
| Grafana            | Monitoring       | 3000  | —          | admin/admin default |
| Grocy              | Household        | 9283  | —          | groceries, chores, batteries |
| Grist              | Spreadsheet      | 8484  | —          | relational spreadsheet with Python |
| HedgeDoc           | Markdown editor  | 3000  | —          | |
| HitKeep            | Bookmarks        | 8080  | caddy      | Single container |
| Home Assistant     | Smart home       | 8123  | caddy      | slow startup (~50s) |
| Homer              | Dashboard        | 8080  | caddy      | Static dashboard, no DB |
| Huginn             | Automation       | 3000  | caddy      | Task automation + postgres |
| Immich             | Photos           | 2283  | —          | Google Photos alternative |
| InfluxDB           | Time-series DB   | 8086  | caddy      | Time-series database |
| IT-Tools           | Developer tools  | 8083  | —          | container listens on 80, not 8080 |
| Jellyfin           | Media server     | 8096  | —          | |
| Jitsi Meet         | Video conf       | 80/443| —          | uses :unstable tags; nginx permission bug |
| Kavita             | Reading          | 5000  | —          | comics/manga reader |
| Keycloak           | IAM/SSO          | 8080  | caddy      | OAuth2/OIDC identity + postgres |
| Karakeep           | Bookmarks        | 3000  | caddy      | Bookmarks + postgres + meilisearch |
| Komga              | Comics/manga     | 25600 | —          | |
| Kopia              | Backup           | 51515 | caddy      | Encrypted backup to cloud/local |
| Kestra             | Automation       | 8080  | caddy      | Workflow automation + postgres |
| Khoj               | AI assistant     | 42110 | caddy      | AI assistant + postgres |
| Langflow           | AI workflows     | 7860  | caddy      | AI workflow builder + postgres |
| Lemmy              | Link aggregator  | 1234  | —          | pinned dessalines/lemmy:0.19.11 |
| LibreChat          | AI chat          | 3080  | caddy      | ChatGPT alternative + MongoDB |
| Linkding           | Bookmarks        | 9090  | —          | |
| Linkwarden         | Bookmarks        | 3000  | —          | |
| LobeChat           | AI chat          | 3210  | caddy      | ChatGPT alternative + postgres |
| Lychee             | Photos           | 8080  | caddy      | Photo manager + postgres |
| Listmonk           | Newsletter       | 9000  | —          | needs --install flag on first run |
| LocalAI            | AI inference     | 8080  | caddy      | Local LLM inference server |
| Mastodon           | Social network   | 3000  | —          | |
| Matomo             | Analytics        | 8080  | caddy      | App + MariaDB |
| Maybe Finance      | Personal finance | 3000  | —          | |
| Mealie             | Recipes          | 9925  | —          | SQLite by default |
| Meilisearch        | Search           | 7700  | —          | |
| MongoDB            | Database         | 27017 | caddy      | Document database |
| Miniflux          | RSS reader       | 8080  | caddy      | RSS reader + postgres |
| MinIO             | Object store     | 9000  | caddy      | S3-compatible storage |
| MeTube             | Media download   | 8081  | —          | YouTube downloader |
| Memos              | Notes            | 5230  | —          | |
| Metabase           | BI               | 3000  | —          | |
| Middleware         | Analytics        | 3333  | caddy      | Engineering metrics |
| Mattermost         | Team chat        | 8065  | —          | Slack alternative + postgres |
| Nextcloud          | File sync        | 8080  | —          | |
| Navidrome          | Music            | 4533  | —          | music streaming server |
| NocoDB             | Database         | 8080  | —          | Airtable alternative + postgres |
| Navidrome          | Music            | 4533  | caddy      | music streaming server |
| Ntfy               | Notifications    | 8080  | caddy      | Push notification server |
| Offen              | Analytics        | 3000  | caddy      | single container, privacy-first |
| Ombi               | Media requests   | 3579  | —          | Plex/Jellyfin requests |
| OneTimeSecret      | Secret sharing   | 3000  | caddy      | Self-destructing secret links |
| Organizr           | Dashboard        | 9983  | —          | HTPC dashboard |
| Open-WebUI         | AI chat          | 3000  | —          | |
| Outline            | Knowledge base   | 3000  | —          | |
| Paperless-ngx      | Document mgmt    | 8000  | —          | |
| PhotoPrism         | Photos           | 2342  | caddy      | Google Photos alternative |
| Pi-hole            | DNS ad-block     | 8080  | —          | |
| Pingvin Share      | File sharing     | 3000  | —          | WeTransfer alternative |
| Planka             | Kanban           | 1337  | caddy      | Kanban board + postgres |
| Plausible          | Analytics        | 8000  | —          | |
| Portainer          | Docker mgmt      | 9000  | —          | container management UI |
| PostHog            | Product analytics| 8000  | —          | |
| Postiz App         | Social scheduler | 4007  | —          | 6 containers: app + postgres + redis + temporal + ES |
| Prowlarr           | Indexer manager  | 9696  | caddy      | Indexer manager |
| Redash             | BI               | 5000  | —          | |
| Readeck            | Bookmarks        | 8000  | caddy      | Bookmarks + postgres |
| Restic REST Server | Backup           | 8000  | caddy      | Backup server |
| Rocket.Chat        | Chat             | 3000  | —          | needs manual `rs.initiate()` on mongo |
| Rallly             | Scheduling       | 3000  | caddy      | Date polls + postgres |
| ROMM              | ROM manager      | 8080  | —          | |
| RustFS            | File storage     | 3001  | —          | |
| Rybbit            | Analytics        | 8080  | —          | Clickhouse config bind mount |
| S4Core            | File sharing     | 8080  | —          | |
| Semaphore         | Ansible UI       | 3000  | —          | fixed DB_DIALECT typo |
| Shaper            | Dashboards       | 8080  | caddy      | DuckDB analytics |
| Shlink            | URL shortener    | 8080  | caddy      | URL shortener + postgres |
| SimpleLogin       | Email alias      | 8080  | caddy      | Email alias + postgres (needs SMTP/DKIM) |
| Statistics for Strava | Fitness      | 8080  | —          | waits for Strava API credentials |
| Strapi            | CMS              | 1337  | —          | uses naskio/strapi instead of strapi |
| Supabase          | Backend platform | 8000  | —          | 10 containers; needs role passwords set via supabase_admin |
| Supabase-PostHog  | Analytics + Backend | 8000 | —          | Supabase + PostHog combined |
| Superset          | BI               | 8088  | —          | needs manual `superset fab create-admin` + `db upgrade` + `init` |
| SurrealDB         | Database         | 8000  | caddy      | Multi-model database |
| Synapse           | Matrix chat      | 8008  | —          | |
| Syncthing         | File sync        | 8384  | —          | P2P file synchronization |
| Tandoor           | Recipes          | 8080  | —          | fixed port mapping 8080->80 (nginx) |
| Trilium           | Notes            | 8081  | —          | |
| Typebot           | Chatbots         | 3001  | caddy      | Conversational form builder + postgres |
| Umami             | Analytics        | 3000  | —          | |
| UptimeKuma        | Monitoring       | 3001  | —          | |
| UrBackup           | Backup           | 55414 | caddy      | Backup server |
| Vaultwarden       | Password mgr     | 8080  | —          | with Nginx Proxy Manager |
| Vikunja           | Task management  | 3456  | caddy      | Project management + postgres |
| Wallabag          | Read-it-later    | 80    | —          | + postgres + redis |
| WordPress         | CMS              | 8080  | —          | uses image: wordpress (no tag) + mysql:8.0 |
| Wger              | Fitness          | 8000  | caddy      | Fitness tracker + postgres |
| Windmill          | Automation       | 8000  | caddy      | Workflow automation + postgres |
| Zitadel           | IAM/SSO          | 8080  | —          | ExternalDomain must match server IP |
| Zipline           | File sharing     | 3000  | caddy      | File sharing + postgres |
| Zammad            | Ticketing        | 80    | caddy      | Ticketing + postgres + redis + memcached |
| Zulip             | Team chat        | 80    | caddy      | Team chat + postgresql |

### Pre-existing (configured, not re-deployed)

| Project       | Type         | Notes |
|---------------|--------------|-------|
| ArchiveBox    | Web archive  | |
| AstrBot       | AI chatbot   | |
| ComfyUI       | AI image gen | Cloud: container runs but not reachable |
| Coolify       | PaaS         | Cloud: local-exec provisioner error |
| Countly Server| Analytics    | 4 containers running; nginx config needs manual SCP |
| Floci         | File sharing | |
| GoAccess      | Analytics    | Config bind-mount files not copied to server |
| HitKeep       | Bookmarks    | Single container |
| Linkding      | Bookmarks    | Single container |
| Matomo        | Analytics    | App + MariaDB |
| Audiobookshelf| Audiobooks   | Single container |
| Cal.com       | Scheduling   | Calendly alternative + postgres |
| Calibre-web   | E-books      | linuxserver/calibre-web |
| changedetection.io | Monitoring | Website change detection |
| Gotify        | Notifications| Push notification server |
| Homer         | Dashboard    | Static dashboard, no DB |
| Kopia         | Backup       | Backup solution, no DB |
| Memos         | Notes        | Lightweight note-taking |
| Mealie        | Recipes      | Recipe manager |
| n8n           | Automation   | Workflow automation + postgres |
| One Time Secret | Secret sharing | Self-destructing secret links |
| Rallly        | Scheduling   | Date polls + postgres |
| Screego       | Screen sharing| WebRTC screen sharing |
| Stirling-PDF  | PDF tools    | PDF manipulation, no DB |
| Typebot       | Chatbots     | Conversational form builder + postgres |
| Woodpecker CI | CI/CD        | CI/CD pipeline engine |
| Audiobookshelf| Audiobooks   | Single container |
| BookStack     | Documentation| Wiki + MariaDB |
| Caddy         | Web server   | Auto-HTTPS reverse proxy |
| CrowdSec      | Security     | Threat detection |
| Duplicati     | Backup       | Encrypted backup to cloud/local |
| Frigate       | Video NVR    | AI object detection |
| FreshRSS      | RSS reader   | Self-hosted RSS |
| Home Assistant| Smart home   | Home automation platform |
| Immich        | Photos       | Google Photos alternative |
| Keycloak      | IAM/SSO      | OAuth2/OIDC/SAML identity |
| Meilisearch   | Search       | Lightning-fast search engine |
| MinIO         | Object store | S3-compatible storage |
| Speedtest Tracker | Monitoring| Internet speed tracking |
| Syncthing     | File sync    | P2P Dropbox alternative |
| Traefik       | Reverse proxy| Auto-discovery proxy |
| WireGuard     | VPN          | Modern VPN |
| Chatwoot      | Support      | Customer support + REST API + webhooks |
| Directus      | Headless CMS | REST + GraphQL API |
| Hanko         | Auth         | Passkeys + REST API |
| Infisical     | Secrets      | Secret management + REST API |
| Jellyseerr    | Media requests| Media request management + REST API |
| Tautulli      | Plex monitor | Plex analytics + REST API |

### Known image issues

| Project      | Issue | Workaround |
|-------------|-------|-----------|
| discourse    | `discourse/base` doesn't exist | Use `discourse/discourse:latest` |
| jitsi/web    | `:latest` tag doesn't exist | Use `jitsi/web:unstable` (and prosody, jicofo, jvb) |
| strapi       | `strapi:latest` doesn't exist | Use `naskio/strapi:latest` |
| wordpress    | `wordpress:latest` exists as `wordpress` | Use `wordpress` (no tag) |
| druid        | `apache/druid:38.0.0` doesn't exist | Use `apache/druid:31.0.0` |
| lemmy        | `dessalines/lemmy:latest` never existed | Use `dessalines/lemmy:0.19.11` |
| mysql:8-alpine | No such image | Use `mysql:8.0` or `postgres:16-alpine` |

### Common stacker.yml issues

| Issue | Cause | Fix |
|-------|-------|-----|
| Service labels stripped | Stacker doesn't pass `services[].labels` to compose | Use app.env vars or nginx proxy instead |
| serde_yaml 0.9 quoting | Round-trip strips quotes, adds `null`/`[]` | No fix yet; PR pending |
| Bind mount files not found | File paths resolve relative to compose location on remote | Use Dockerfile COPY instead of bind mounts |
| `:latest` images not found | Many projects have no `latest` tag | Pin to specific version or tag |

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

Last updated: 2026-08-25 — 244 projects configured, 110 tested and verified on
Ubuntu 26.04. Proxy support: traefik, caddy, nginx-proxy-manager.

---

<p align="center">
  <sub>⭐ Star this repo if it saved you a weekend of Docker Compose wrangling.</sub><br>
  <sub>Built with <a href="https://github.com/trydirect/stacker">Stacker</a> · Contributions welcome — one app per PR.</sub>
</p>
