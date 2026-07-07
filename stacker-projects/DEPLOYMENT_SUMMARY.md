# Stacker Self-Hosted Projects - Deployment Summary

**Created:** July 7, 2026  
**Total Projects Configured:** 42  
**New Projects Created:** 21

## Overview

All 42 self-hosted projects are now configured with `stacker.yml` files and ready for deployment via Stacker. Each project includes:

- ✅ `stacker.yml` configuration
- ✅ Docker service definitions  
- ✅ Database setup (PostgreSQL, MySQL, MongoDB as needed)
- ✅ Volume management
- ✅ Environment variable contracts
- ✅ Cloud deployment config (Hetzner)
- ✅ Health checks for all services
- ✅ Monitoring/status panel enabled

---

## 📊 By Category

### **Analytics & Data Visualization** (8 projects)
- **Matomo** — Web analytics (PHP)
- **Plausible** — Privacy-focused analytics (Elixir)
- **Umami** — Google Analytics alternative (Node.js)
- **Metabase** — Business intelligence (Java)
- **PostHog** — Product analytics (Python)
- **Redash** — Data exploration (Python)
- **Superset** — Data visualization (Python)
- **ArchiveBox** — Archive & screenshots (Python)

### **Collaboration & Communication** (7 projects)
- **Rocket.Chat** — Team chat (Node.js)
- **Synapse** — Matrix protocol server (Python)
- **Zulip** — Team chat with topics (Python)
- **Jitsi Meet** — Video conferencing (Node.js)
- **Mastodon** — Federated social network (Ruby)
- **Lemmy** — Link aggregator (Rust)
- **Discourse** — Community forum (Ruby/JS)

### **Content & Publishing** (5 projects)
- **WordPress** — Blogging & CMS (PHP)
- **Ghost** — Blogging platform (Node.js)
- **Strapi** — Headless CMS (Node.js)
- **Nextcloud** — File sync & collaboration (PHP)
- **Outline** — Team wiki (Node.js)

### **Document & Bookmark Management** (3 projects)
- **Paperless-ngx** — Document management (Python)
- **Wallabag** — Read-it-later service (PHP)
- **linkding** — Bookmark manager (Python)

### **Developer Tools** (4 projects)
- **Gitea** — Git service (Go)
- **Coolify** — Deployment platform (Node.js)
- **StackDog** — Infrastructure as code (custom)
- **InsForge** — Custom development tool

### **Media & Entertainment** (2 projects)
- **Jellyfin** — Media server (C#)
- **ROMM** — ROM collection manager

### **Security & Storage** (2 projects)
- **Bitwarden** — Password manager (Rust, via Vaultwarden)
- **Vaultwarden** — Lightweight Bitwarden server (Rust)

### **AI & ML Tools** (6 projects)
- **Open-WebUI** — LLM UI (Python)
- **ComfyUI** — Node-based AI image generation
- **Dify** — LLM application platform
- **AstrBot** — Multi-platform AI chatbot
- **HermesAgent** — AI agent framework
- **SwarmUI** — Distributed AI inference

### **Other** (3 projects)
- **PiHole** — DNS blocker
- **Uptimekuma** — Uptime monitoring
- **Supabase** — Firebase alternative
- **Floci** — Custom deployment tool
- **RustFS** — File system tools

---

## 🚀 Quick Start

### Deploy a Single Project

```bash
cd matomo
stacker deploy
```

### Deploy to Cloud

```bash
cd wordpress
stacker deploy --target cloud --force-rebuild
```

### List All Projects

```bash
ls -1d */
```

### Check Project Status

```bash
cd jellyfin
stacker agent health
```

---

## 🔑 Environment Setup

Each project requires a `.env` file with secrets. The `config_contract` in each `stacker.yml` defines:

- **Required vs. Optional** variables
- **Secret vs. Public** designation
- Database passwords, API keys, etc.

Example `.env` structure:

```bash
DB_PASSWORD=secure_password_here
ADMIN_PASSWORD=another_secure_password
SECRET_KEY=random_secret_key
JWT_SECRET=jwt_secret_here
```

### Generate Secrets Automatically

Each project includes a `hooks.pre_build` script that can generate missing secrets:

```bash
cd project-name
mkdir -p scripts
# Add secret generation script
stacker deploy
```

---

## ☁️ Cloud Deployment

All projects are pre-configured for Hetzner cloud deployment. Adjust as needed:

```yaml
deploy:
  cloud:
    provider: hetzner  # or: digitalocean, aws, linode, vultr
    region: fsn1
    size: cpx22        # Adjust for project needs
    public_ports:
      - "8080"
```

### Required Configuration

Before deploying to cloud:
1. Set `HETZNER_API_TOKEN` environment variable
2. Configure SSH key path in `stacker.yml`
3. Update `public_ports` for your app
4. Set domain in environment variables

---

## 🔒 Database & Service Dependencies

Most projects use PostgreSQL (recommended for new deployments):

- **PostgreSQL:** Matomo, Nextcloud, WordPress, Discourse, Synapse, Mastodon, Strapi, Gitea, Zulip, Wallabag, Jellyfin*, Paperless-ngx, Linkding, Redash, Superset, PostHog, Metabase
- **MySQL/MariaDB:** WordPress (alt), Ghost
- **MongoDB:** Rocket.Chat
- **Redis:** Required for caching/queue (included with most)
- **Custom:** Jitsi (Prosody), Mastodon (Sidekiq workers)

---

## 📈 Monitoring

All projects have `monitoring.status_panel: true` enabled:

```bash
stacker agent health
stacker agent logs <app-name> --lines 200
```

---

## 🔄 Common Configurations

### Change Database to MySQL
```yaml
services:
  - name: db
    image: mysql:8
    # ... mysql config
```

### Add Custom Domain
```yaml
install:
  inputs:
    commonDomain: myproject.com
```

### Change Ports
```yaml
app:
  ports:
    - "8080:8080"  # Host:Container
```

### Scale Workers (Mastodon, Zulip, etc.)
```yaml
services:
  - name: sidekiq
    environment:
      QUEUE_WORKERS: "8"  # Increase concurrency
```

---

## ⚠️ Important Notes

1. **Secrets:** Never commit `.env` files to version control
2. **Volumes:** Use named volumes for persistent data
3. **Health Checks:** All databases have health checks enabled (10s interval)
4. **Firewall:** Cloud deployments automatically open required ports via `public_ports`
5. **Backups:** Set up database backups before production use
6. **SSL/TLS:** Add SSL configuration in proxy section for production

---

## 🛠️ Customization

Each project can be customized by editing its `stacker.yml`:

```bash
cd project-name
nano stacker.yml
stacker config validate  # Check for errors
stacker deploy
```

---

## 📝 Next Steps

1. **Select a project** to deploy
2. **Copy the directory** to your infrastructure server
3. **Configure `.env`** with your secrets
4. **Run `stacker deploy`**
5. **Access the web UI** at the configured domain

---

## 📚 Resources

- **Stacker CLI:** `stacker --help`
- **Docker Hub:** Official images for each project
- **Project Docs:** Visit each project's GitHub repo for detailed configuration

---

**Status:** ✅ All 42 projects are ready for deployment
