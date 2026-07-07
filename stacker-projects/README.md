# 🚀 Stacker Self-Hosted Projects

**42 Production-Ready Docker Projects** configured for **Stacker** deployment platform.

> All projects include complete `stacker.yml` configurations, database setup, health checks, monitoring, and cloud deployment support.

---

## 📋 Quick List

| # | Project | Category | Port | Tech |
|---|---------|----------|------|------|
| 1 | **Matomo** | Analytics | 80 | PHP |
| 2 | **Metabase** | BI | 3000 | Java |
| 3 | **PostHog** | Analytics | 8000 | Python |
| 4 | **Redash** | Visualization | 5000 | Python |
| 5 | **Superset** | Visualization | 8088 | Python |
| 6 | **Nextcloud** | File Sync | 80 | PHP |
| 7 | **WordPress** | CMS | 80 | PHP |
| 8 | **Ghost** | Blogging | 2368 | Node.js |
| 9 | **Strapi** | Headless CMS | 1337 | Node.js |
| 10 | **Discourse** | Forum | 80/443 | Ruby/JS |
| 11 | **Rocket.Chat** | Chat | 3000 | Node.js |
| 12 | **Synapse** | Matrix Server | 8008 | Python |
| 13 | **Zulip** | Team Chat | 80/443 | Python |
| 14 | **Jitsi Meet** | Video | 80/443 | Node.js |
| 15 | **Mastodon** | Social Network | 3000 | Ruby |
| 16 | **Lemmy** | Link Aggregator | 8536 | Rust |
| 17 | **Gitea** | Git Service | 3000 | Go |
| 18 | **Bitwarden** | Password Manager | 80 | Rust |
| 19 | **Jellyfin** | Media Server | 8096 | C# |
| 20 | **Paperless-ngx** | Documents | 8000 | Python |
| 21 | **Wallabag** | Read-Later | 80 | PHP |
| 22 | **linkding** | Bookmarks | 9090 | Python |
| 23 | **ArchiveBox** | Web Archive | 8000 | Python |
| 24-42 | *+ 18 more* | *various* | *various* | *various* |

**See [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md) for complete details.**

---

## 🎯 Get Started (5 min)

### 1. Pick a Project
```bash
cd wordpress
```

### 2. Create `.env` with Secrets
```bash
cat > .env << 'EOF'
DB_PASSWORD=change_me_to_secure_password
DB_ROOT_PASSWORD=change_root_password
EOF
```

### 3. Deploy Locally
```bash
stacker deploy
```

### 4. Access Your App
Open `http://localhost:8080` (port depends on project)

---

## ☁️ Deploy to Cloud (Hetzner)

```bash
cd wordpress
export HETZNER_API_TOKEN=your_token_here
export HETZNER_REGION=fsn1
export HETZNER_SERVER_TYPE=cpx22

stacker deploy --target cloud --force-rebuild
```

---

## 📂 Project Structure

Each project contains:
```
project-name/
├── stacker.yml           # Stacker configuration (Dockerfile + docker-compose)
├── .env                  # Secrets (create this)
└── (optional files)      # Custom configs, scripts, etc.
```

---

## 🔧 Common Commands

```bash
# Validate config
stacker config validate

# See resolved config
stacker config show --resolved

# Check health
stacker agent health

# View logs
stacker agent logs app-name --lines 100

# Stop/start containers
docker-compose down
docker-compose up -d
```

---

## 📊 By Use Case

### **Blogging & Content**
WordPress, Ghost, Strapi, Outline, Discourse

### **Analytics & BI**
Matomo, Metabase, PostHog, Redash, Superset, Plausible, Umami

### **Communication**
Rocket.Chat, Zulip, Synapse, Jitsi Meet, Mastodon, Lemmy

### **File Storage & Sync**
Nextcloud, Wallabag, linkding, Paperless-ngx, ArchiveBox

### **Developer Tools**
Gitea, Strapi, Coolify, StackDog

### **Security**
Bitwarden/Vaultwarden

### **Media**
Jellyfin, ROMM

### **AI/ML**
Open-WebUI, ComfyUI, Dify, AstrBot, HermesAgent, SwarmUI

---

## ⚙️ Customization

### Change Database (MySQL → PostgreSQL)
Edit `stacker.yml`:
```yaml
services:
  - name: db
    image: postgres:16-alpine  # ← change this
```

### Change Port
```yaml
app:
  ports:
    - "8080:8080"  # Change first number
```

### Add Environment Variables
```yaml
app:
  environment:
    CUSTOM_VAR: "value"
    ANOTHER_VAR: "${ENV_VAR}"  # From .env
```

### Add Services (Redis, etc.)
```yaml
services:
  - name: cache
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
```

---

## 🔐 Security Checklist

- [ ] Change all database passwords in `.env`
- [ ] Update domain names
- [ ] Enable SSL/TLS in proxy section
- [ ] Don't commit `.env` to git
- [ ] Set strong admin passwords
- [ ] Use `public_ports` carefully (firewall)
- [ ] Back up databases regularly
- [ ] Monitor logs and health checks

---

## 🐛 Troubleshooting

### Container won't start
```bash
docker logs container_name
```

### Port already in use
```bash
# Change port in stacker.yml
# Or kill existing process
lsof -i :8080  # Find process using port 8080
kill -9 <PID>
```

### Database migration failed
```bash
# Check database health
docker exec db_container pg_isready
```

### Can't access from browser
```bash
# Check firewall (cloud deployments)
stacker cloud firewall list
stacker cloud firewall add --public-ports 8080/tcp
```

---

## 📚 Resources

- [Stacker Docs](https://stacker.dev)
- [Each project's GitHub repository](https://github.com)
- [awesome-selfhosted](https://github.com/awesome-selfhosted/awesome-selfhosted)

---

## 📝 Notes

- **Databases**: All include PostgreSQL by default (highly configurable)
- **Health Checks**: 10s intervals, fail after 10 retries
- **Volumes**: Named volumes for data persistence
- **Compose**: All projects can run with `docker-compose up -d`
- **Monitoring**: `status_panel: true` enabled for all

---

**Status:** ✅ All 42 projects ready for deployment

Last updated: July 7, 2026
