# Stacker Self-Hosted Projects

All projects include complete `stacker.yml` configurations, database setup, health checks, and deployment support for local, own server, and cloud environments.


## Quick Start

### 1. Pick a Project
```bash
cd umami  # or your choice
```

### 2. Deploy


#### Local Deployment
```bash
stacker deploy
# Access at http://localhost:PORT (see stacker.yml for port)
```


#### Own Server Deployment
```bash
stacker deploy --target server \
  --server-host your-server.com \
  --server-user root \
  --server-port 22 \
  --server-ssh-key ~/.ssh/id_ed25519
```


#### Cloud Deployment (Hetzner)

```bash
export HETZNER_API_TOKEN=your_token_here
stacker deploy --target cloud --force-rebuild
# Automatically opens firewall ports
```


### Local Deployment (Development)

Perfect for testing on your machine.



**Prerequisites:**
- Docker installed
- Docker Compose installed
- Stacker CLI installed


**Useful Local Commands:**


```bash
# View logs (live)
docker-compose logs -f app_name

# SSH into container
docker exec -it app_name sh

# Check database
docker exec db_container psql -U postgres -d dbname

# Restart everything
docker-compose restart

# Remove everything (data lost!)
docker-compose down -v
```

---


### Own Server Deployment (Production)

Deploy to a dedicated Linux server you control.


**Prerequisites:**
- Linux server (Ubuntu 20.04+, Debian 11+, etc.)
- SSH access with key-based auth
- Docker installed on server
- 2GB+ RAM, 20GB+ disk




**Full Example: Deploy Ghost to Your Server**

```bash
# 1. Generate secrets locally
cd ghost
./scripts/generate-secrets.sh

# 2. Configure your .env
nano .env
# Update: GHOST_URL to your domain

# 3. Deploy to your server
stacker deploy --target server \
  --server-host example.com \
  --server-user root \
  --server-port 22 \
  --server-ssh-key ~/.ssh/id_ed25519

# 4. Monitor deployment (on your machine)
stacker status

# 5. Check container on server
ssh root@example.com docker-compose ps
```

**What Happens During Deployment:**

1. Uploads compressed config bundle to server
2. Creates `.stacker/` directory on server
3. Generates `docker-compose.yml` from `stacker.yml`
4. Runs `docker-compose up -d` on server
5. Health checks confirm services are ready
6. Runs post-deploy hooks (if configured)

**Manual SSH to Server (if needed):**

```bash
# SSH into server
ssh root@example.com

# Navigate to app directory
cd /root/ghost

# Check logs
docker-compose logs app

# Rebuild and redeploy
docker-compose down
docker-compose up -d

# Update app (pull latest image)
docker-compose pull
docker-compose up -d
```

**Using Custom SSH Key:**

```bash
# If key has different name/path
export SSH_KEY=~/.ssh/custom_key_ed25519
stacker deploy --target server \
  --server-host example.com \
  --server-user ubuntu \
  --server-ssh-key $SSH_KEY
```

**Using Password Auth (not recommended):**

```bash
# Will prompt for password
stacker deploy --target server \
  --server-host example.com \
  --server-user ubuntu
```

---

### ☁️ Cloud Deployment (Hetzner)

Fully automated cloud provisioning.

**Prerequisites:**
- Hetzner Cloud account
- API token from Hetzner console
- SSH key registered with Hetzner

**Full Example: Deploy Nextcloud to Hetzner**

```bash
# 1. Get credentials from Hetzner
# - Go to: https://console.hetzner.cloud/projects
# - Copy API Token
# - Ensure SSH key is added to account

# 2. Generate secrets
cd nextcloud
./scripts/generate-secrets.sh

# 3. Configure
nano .env
# Update: COMMON_DOMAIN to your domain

# 4. Deploy to cloud (creates NEW server)
export HETZNER_API_TOKEN=your_api_token_here
stacker deploy --target cloud \
  --force-rebuild \
  --force-new
# Takes 5-10 minutes

# 5. Get server IP
stacker status

# 6. Configure DNS
# Add A record: nextcloud.example.com → server_ip

# 7. Access application
open https://nextcloud.example.com

# 8. Redeploy to same server (update config)
stacker deploy --target cloud --force-rebuild
# (don't use --force-new, keeps existing server)
```

**Cloud Configuration in stacker.yml:**

```yaml
deploy:
  target: cloud
  cloud:
    provider: hetzner         # or: digitalocean, aws, linode, vultr
    region: fsn1              # Frankfurt; try: ash, nbg1, hel1, etc.
    size: cpx22               # 4 vCPU, 8GB RAM; options: cpx11, cpx21, cpx31
    ssh_key: ~/.ssh/id_ed25519
    public_ports:
      - "80"
      - "443"
      - "3306"  # Example: expose MySQL
```

**Server Size Reference:**

| Size | vCPU | RAM | Price | Best For |
|------|------|-----|-------|----------|
| `cpx11` | 2 | 4GB | €4.5/mo | Small apps, testing |
| `cpx21` | 4 | 8GB | €8/mo | Most apps |
| `cpx22` | 4 | 16GB | €16/mo | Heavy apps (Mastodon, Nextcloud) |
| `cpx31` | 8 | 32GB | €24/mo | Very heavy (multiple apps) |

**Hetzner Regions:**

```
fsn1 = Frankfurt, Germany (default)
nbg1 = Nuremberg, Germany
hel1 = Helsinki, Finland
ash  = Ashburn, USA
hil  = Hillsboro, USA
sjc  = San Jose, USA
sin  = Singapore
```

**Common Cloud Commands:**

```bash
# List all deployments/servers
stacker list

# Check deployment status
stacker status

# Get server info
stacker agent status

# View server logs
stacker agent logs app-name --lines 50

# Add firewall port
stacker cloud firewall add --public-ports 8080/tcp --server-id srv-123

# List firewall rules
stacker cloud firewall list

# SSH into cloud server
ssh root@server_ip

# Redeploy with config changes
stacker deploy --target cloud --force-rebuild

# Delete server (⚠️ data loss!)
stacker cloud destroy --server-id srv-123
```

---

## 🔐 Secret Management

### Auto-Generate Secrets

```bash
# Enter project directory
cd project-name

# Run once (creates .env from .env.example)
./scripts/generate-secrets.sh

# What it generates:
# DB_PASSWORD=a1b2c3d4e5f6g7h8... (32-char hex)
# SECRET_KEY=x9y8z7w6v5u4t3s2... (64-char hex)
# JWT_SECRET=p1q2r3s4t5u6v7w8... (64-char hex)
# etc.
```

### Manual Secret Configuration

```bash
# Edit .env manually
nano .env

# Add environment-specific config
export ENVIRONMENT=production
nano .env

# Or set inline
ADMIN_PASSWORD=your-strong-password \
  stacker deploy --target cloud
```

### Secret Types Generated

| Variable | Method | Length | Used For |
|----------|--------|--------|----------|
| `*_PASSWORD` | `openssl rand -hex 16` | 32 chars | DB/service passwords |
| `*_SECRET*` | `openssl rand -hex 32` | 64 chars | App encryption keys |
| `*_TOKEN` | `openssl rand -base64 32` | 43 chars | Auth tokens |
| `*_KEY` | `openssl rand -hex 32` | 64 chars | Encryption keys |
| `*_BASE` | `openssl rand -hex 64` | 128 chars | Framework keys (Rails, Phoenix) |

### Viewing Generated Secrets

```bash
# Show all secrets
cat .env

# Show specific secret
grep DB_PASSWORD .env

# Verify format
openssl rand -hex 16  # Check what a password looks like
```

---

## ✅ Tested & Verified Projects

Projects that have been deployed and verified working:

| Project | Type | Status | Deployed By | Date |
|---------|------|--------|-------------|------|
| **ArchiveBox** | Web Archive | ✅ Tested | Team | 2026-07-07 |
| **AstrBot** | AI Chatbot | ✅ Tested | Team | 2026-07-07 |
| **Floci** | Deployment | ✅ Tested | Team | 2026-07-07 |
| **Ghost** | Blogging | ✅ Tested | Team | 2026-07-07 |
| **Outline** | Team Wiki | ✅ Tested | Team | 2026-07-07 |
| **Plausible** | Analytics | ✅ Tested | Team | 2026-07-07 |
| **ROMM** | ROM Manager | ✅ Tested | Team | 2026-07-07 |
| **StackDog** | DevOps Tool | ✅ Tested | Team | 2026-07-07 |
| **Umami** | Analytics | ✅ Tested | Team | 2026-07-07 |
| **UptimeKuma** | Monitoring | ✅ Tested | Team | 2026-07-07 |

**Recommendation:** Start with tested projects for production. Use others for testing.

---

## ⚠️ Not Yet Tested Projects

The following projects are configured but not yet verified in production:

**Analytics & BI (4):**
Matomo, Metabase, PostHog, Redash, Superset

**Collaboration (7):**
Rocket.Chat, Synapse, Zulip, Jitsi Meet, Mastodon, Lemmy, Discourse

**Content & CMS (5):**
WordPress, Strapi, Nextcloud, ComfyUI, Dify

**Documents (3):**
Paperless-ngx, Wallabag, linkding

**Developer Tools (2):**
Gitea, Coolify, HermesAgent, insforge

**Media & Storage (2):**
Jellyfin, Bitwarden

**Other (4):**
Open-WebUI, Supabase, SwarmUI, Vaultwarden

**To help test:** Report issues on GitHub or document your deployment experience.

---

## 📂 Project Structure

Each project follows the secure pattern:

```
project-name/
├── .gitignore                    # Protects .env and .stacker/
├── .env.example                  # Template (COMMITTED)
├── .env                          # Secrets (GITIGNORED)
├── stacker.yml                   # Deployment config
├── scripts/
│   └── generate-secrets.sh       # Pre-build hook
└── (other files)
```

---

## 🔧 Common Commands

### Configuration

```bash
# Validate stacker.yml
stacker config validate

# Show resolved config (with all variables)
stacker config show --resolved

# Show specific section
stacker config show --resolved | grep -A 5 "services:"
```

### Deployment

```bash
# Deploy locally
stacker deploy

# Deploy to server
stacker deploy --target server --server-host example.com

# Deploy to cloud
stacker deploy --target cloud --force-rebuild

# Dry run (preview changes)
stacker deploy --dry-run

# Force rebuild (refresh all images)
stacker deploy --force-rebuild

# Skip hooks
stacker deploy --no-hooks
```

### Monitoring

```bash
# Check deployment status
stacker status

# Check agent health
stacker agent health

# View logs (last 100 lines)
stacker agent logs app_name --lines 100

# Live logs
docker-compose logs -f

# List containers
docker-compose ps

# Get container details
docker ps -a
```

### Docker Operations

```bash
# Stop all containers
docker-compose down

# Start all containers
docker-compose up -d

# Restart specific service
docker-compose restart db

# View logs
docker-compose logs app_name

# SSH into container
docker exec -it app_name sh

# Rebuild image
docker-compose build --no-cache

# Prune unused resources
docker system prune -a
```

---

## ⚙️ Customization

### Change Database (MySQL → PostgreSQL)

Edit `stacker.yml`:
```yaml
services:
  - name: db
    image: postgres:16-alpine      # Change from mysql:8 to this
    environment:
      POSTGRES_PASSWORD: "${DB_PASSWORD}"
      POSTGRES_DB: myapp
```

### Change Port

```yaml
app:
  ports:
    - "8080:8080"  # External:Internal (change 8080 to your port)
```

### Add Environment Variables

```yaml
app:
  environment:
    CUSTOM_VAR: "static_value"
    DYNAMIC_VAR: "${FROM_ENV_FILE}"  # From .env
```

### Add Redis Cache

```yaml
services:
  - name: redis
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"  # Not exposed to network
    volumes:
      - redis_data:/data
```

---

## 🔒 Security Checklist

Before deploying:

- [ ] Generated secrets with `./scripts/generate-secrets.sh`
- [ ] Updated domain names in `.env`
- [ ] Changed database passwords from template
- [ ] Used strong admin passwords
- [ ] Never committed `.env` to git (`.gitignore` protects it)
- [ ] For cloud: added `public_ports` for required ports only
- [ ] For cloud: configured firewall rules
- [ ] Set up database backups (daily minimum)
- [ ] Configured SSL/TLS certificates
- [ ] Enabled health checks (all included)
- [ ] Set log retention policies

**Never commit to git:**
```
.env              # Secrets
.stacker/         # Generated config
.env.local        # Local overrides
```

---

## 🐛 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs container_name

# Check environment
docker inspect container_name | grep -A 20 "Env"

# Verify image exists
docker images | grep image_name
```

### Port Already in Use

```bash
# Find what's using the port
lsof -i :8080
netstat -tulpn | grep 8080

# Kill the process
kill -9 <PID>

# Or change port in stacker.yml
```

### Database Connection Failed

```bash
# Check if DB is ready
docker logs db_container

# Manual check
docker exec db_container pg_isready

# Wait for health check
docker-compose ps  # Look at "Status"
```

### Can't Access from Browser

**Local:**
```bash
# Verify port is open
netstat -tulpn | grep 8080

# Check firewall
sudo ufw status
```

**Cloud:**
```bash
# Add missing port to firewall
stacker cloud firewall add --public-ports 8080/tcp

# List firewall rules
stacker cloud firewall list

# Verify from outside
curl -v http://server-ip:8080
```

### Database Migration Failed

```bash
# Check DB logs
docker-compose logs db

# Verify database exists
docker exec db_container psql -l

# Manual migration (if needed)
docker-compose exec app ./manage.py migrate
```

### High Memory Usage

```bash
# Check container memory
docker stats

# Limit in docker-compose.yml
services:
  app:
    mem_limit: 512m
    memswap_limit: 1g
```

---

## 📊 By Use Case

### **Blogging & Content**
WordPress, Ghost, Strapi, Outline, Discourse

### **Analytics & BI**
Matomo, Metabase, PostHog, Redash, Superset, Plausible ✅, Umami ✅

### **Communication**
Rocket.Chat, Zulip, Synapse, Jitsi Meet, Mastodon, Lemmy

### **File Storage & Sync**
Nextcloud, Wallabag, linkding, Paperless-ngx, ArchiveBox ✅

### **Developer Tools**
Gitea, Strapi, Coolify, StackDog ✅

### **Security & Passwords**
Bitwarden, Vaultwarden

### **Media**
Jellyfin, ROMM ✅

### **AI/ML**
Open-WebUI, ComfyUI, Dify, AstrBot ✅, HermesAgent, SwarmUI

### **Monitoring**
PiHole, UptimeKuma ✅

---

## 📚 Resources

| Resource | Link | For |
|----------|------|-----|
| Stacker Docs | https://stacker.dev | Official docs |
| awesome-selfhosted | https://github.com/awesome-selfhosted/awesome-selfhosted | Project list |
| Docker Hub | https://hub.docker.com | Container images |
| Hetzner Docs | https://docs.hetzner.cloud | Cloud provider |
| Full Documentation | See INDEX.md, PROJECTS_READY.md | This repo |

---

## 📝 Project Files Guide

| File | Purpose | Audience |
|------|---------|----------|
| **README.md** (this file) | Quick start & deployment examples | All users |
| **INDEX.md** | Navigation & project matrix | First-time users |
| **PROJECTS_READY.md** | Deployment workflow & troubleshooting | DevOps engineers |
| **DEPLOYMENT_SUMMARY.md** | All projects by category | Project planners |
| **stacker.yml** (per project) | Deployment configuration | DevOps/developers |
| **scripts/generate-secrets.sh** | Auto-generate secrets | Pre-deployment |

---

## ✅ Deployment Checklist

Before going live:

- [ ] ✅ Pick a tested project (start here)
- [ ] ✅ Run `./scripts/generate-secrets.sh`
- [ ] ✅ Review `.env` for correctness
- [ ] ✅ Test locally: `stacker deploy`
- [ ] ✅ Verify health checks: `stacker agent health`
- [ ] ✅ Backup data sources if needed
- [ ] ✅ For cloud: get Hetzner API token
- [ ] ✅ For cloud: set domain in `.env`
- [ ] ✅ For cloud: `stacker deploy --target cloud`
- [ ] ✅ Configure DNS for your domain
- [ ] ✅ Test from browser
- [ ] ✅ Set up monitoring/backups

---

**Status:** ✅ 10/42 projects tested, 32 awaiting verification  
**Last Updated:** July 7, 2026  
**Next Step:** Pick a tested project and deploy!

See **[INDEX.md](INDEX.md)** for full navigation.


## 📋 Project Status

| Status | Count | Examples |
|--------|-------|----------|
| ✅ **Tested** | 10 | ArchiveBox, AstrBot, Floci, Ghost, Outline, Plausible, ROMM, StackDog, Umami, UptimeKuma |
| ⚠️ **Not Yet Tested** | 32 | Bitwarden, Coolify, Dify, Discourse, Gitea, Jellyfin, Mastodon, Matomo, Metabase, NextCloud, PostHog, Redash, Rocket.Chat, Strapi, Superset, Synapse, WordPress, Zulip, & 14 more |


---
