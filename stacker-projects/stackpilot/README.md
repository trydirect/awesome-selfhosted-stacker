# StackPilot

[![Deploy to TryDirect](https://img.shields.io/badge/Deploy_to-TryDirect-blue)](https://try.direct/quick-deploy?source=github&repo=trydirect/awesome-selfhosted-stacker&path=stacker-projects/stackpilot&ref=main)

**Self-hosted AI website support assistant** — a fully functional RAG-based chat widget that learns from your data, deployable with a single command.

```
┌─────────────────────────────────────────────────────────────┐
│                     WEBSITE (any site)                      │
│  <script src="stackpilot.try.direct/widget.js"></script>    │
└──────────────────────┬──────────────────────────────────────┘
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  STACKPILOT API (FastAPI)                   │
│  • Widget endpoint  • Admin dashboard  • RAG pipeline       │
└───┬──────────┬──────────┬──────────┬────────────────────────┘
    ▼          ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐
│Postgres│ │ Redis  │ │Ollama  │ │    n8n     │
│+pgvec  │ │        │ │        │ │            │
└────────┘ └────────┘ └────────┘ └────────────┘
```

---

## Quick Deploy

```bash
stacker install stackpilot
stacker deploy --target cloud --key htz-0
```

---

## Features

- **Embeddable chat widget** — one `<script>` tag adds AI support to any website
- **RAG-powered answers** — semantic search over your knowledge base using pgvector
- **Website crawler** — automatically ingests your site content into the knowledge base
- **Self-hosted AI** — runs Ollama locally, no OpenAI/Anthropic API keys needed
- **Conversation learning** — stores chat history, tracks feedback, improves over time
- **Workflow automation** — escalates low-confidence answers via n8n webhooks
- **Admin dashboard** — manage knowledge base, view conversations, pull models
- **Production-ready** — Nginx Proxy Manager with auto-SSL, health checks, status panel

---

## Tech Stack

| Service | Image | Purpose |
|---------|-------|---------|
| **app** | Custom Python (FastAPI) | API, RAG pipeline, admin dashboard, widget |
| **stackpilot-db** | `pgvector/pgvector:0.8.0-pg16` | Knowledge base vectors + conversation history |
| **stackpilot-redis** | `redis:7-alpine` | Caching, rate limiting, session store |
| **stackpilot-ollama** | `ollama/ollama:latest` | Self-hosted LLM inference + embeddings |
| **stackpilot-n8n** | `n8nio/n8n:latest` | Workflow automation, escalation, notifications |
| **nginx-proxy-manager** | `jc21/nginx-proxy-manager:latest` | Reverse proxy with auto-SSL |

---

## Prerequisites

- A server with Docker and Docker Compose installed
- At least 2GB RAM + 2GB swap (8GB+ recommended for running larger LLMs)
- (Optional) A domain pointed at your server for SSL

**Quick server setup** (installs Docker, creates swap):

```bash
./scripts/setup-server.sh YOUR_SERVER_IP
```

---

## Installation

### Option 1: Deploy with Stacker (recommended)

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/stackpilot

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy to your server
stacker deploy
```

### Option 2: Manual Docker Compose deploy

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/stackpilot

# Copy compose file and build
cp .stacker/docker-compose.yml .
docker compose up -d --build
```

### First Run Checklist

1. **Open the admin dashboard**
   ```
   http://YOUR_SERVER_IP:8080/api/admin/dashboard
   ```

2. **Sign in** with the `ADMIN_PASSWORD` from your `.env` file

3. **Pull AI models** — go to the **Ollama** tab and pull:
   - `llama3.1` — the LLM for generating responses
   - `nomic-embed-text` — the embedding model for semantic search

4. **Build your knowledge base** — go to the **Websites** tab and crawl your website:
   ```
   https://your-website.com
   ```
   Or add documents manually via the **Knowledge Base** tab.

5. **Embed the widget** on your website:
   ```html
   <script src="http://YOUR_SERVER_IP:8080/api/widget/widget.js"></script>
   ```

6. **(Optional) Set up SSL** — configure Nginx Proxy Manager at port `81` to route your domain to the app.

---

## Configuration

All configuration is via environment variables in `.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | auto-generated | Session signing key |
| `DB_PASSWORD` | auto-generated | PostgreSQL password |
| `ADMIN_PASSWORD` | auto-generated | Dashboard login password |
| `N8N_PASSWORD` | auto-generated | n8n basic auth password |
| `OLLAMA_MODEL` | `llama3.1` | LLM model for generating responses |
| `OLLAMA_EMBED_MODEL` | `nomic-embed-text` | Embedding model for vector search |
| `DEPLOY_HOST` | — | Server IP for Stacker deployment |
| `BASE_PATH` | — | Local project path for Stacker |

---

## API Reference

### Widget API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/widget/chat` | Send a message, get an AI response |
| `GET` | `/api/widget/widget.js` | Embeddable chat widget JavaScript |
| `POST` | `/api/widget/feedback` | Submit feedback on a conversation |
| `POST` | `/api/widget/resolve` | Mark a conversation as resolved |

### Admin API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/stats` | Dashboard statistics |
| `GET` | `/api/admin/dashboard` | Admin dashboard HTML |
| `POST` | `/api/admin/login` | Authenticate |
| `POST` | `/api/admin/logout` | Sign out |
| `GET` | `/api/admin/documents` | List knowledge base documents |
| `POST` | `/api/admin/documents` | Add a document |
| `DELETE` | `/api/admin/documents/{id}` | Remove a document |
| `GET` | `/api/admin/websites` | List crawled websites |
| `POST` | `/api/admin/websites` | Register a website |
| `POST` | `/api/admin/websites/crawl` | Start crawling a website |
| `DELETE` | `/api/admin/websites/{id}` | Remove a website |
| `GET` | `/api/admin/conversations` | List conversations |
| `GET` | `/api/admin/ollama/status` | Check Ollama health + installed models |
| `POST` | `/api/admin/ollama/pull` | Pull a new model |

### Webhook API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/webhooks/n8n` | n8n callback for escalation events |
| `POST` | `/api/webhooks/ingest` | External content ingestion endpoint |

---

## How It Works

### Data Flow

```
1. Visitor asks a question on your website
   ↓
2. widget.js sends message to /api/widget/chat
   ↓
3. Query is embedded using nomic-embed-text via Ollama
   ↓
4. pgvector performs cosine similarity search (top-K results)
   ↓
5. Retrieved documents are injected into the prompt as context
   ↓
6. llama3.1 generates a response using the context
   ↓
7. Response is returned to the visitor in real-time
   ↓
8. Conversation is stored for analytics and learning
   ↓
9. If confidence < 0.3 → escalation via n8n webhook
```

### Knowledge Base Pipeline

```
Website URL → Crawler → Text extraction → Chunking (500 tokens)
  → Embedding (nomic-embed-text) → pgvector storage
```

Documents are automatically chunked into 500-token pieces with 100-token overlap for context continuity.

---

## Deployment Targets

### Local

```yaml
deploy:
  target: local
```

### Remote Server (SSH)

```yaml
deploy:
  target: server
  server:
    host: ${DEPLOY_HOST}
    user: root
    ssh_key: ${BASE_PATH}/stacker-project-test
```

### Cloud (Hetzner)

```yaml
deploy:
  target: cloud
  cloud:
    provider: hetzner
    region: fsn1
    size: cpx32
    public_ports:
      - "80"
      - "443"
      - "8080"
      - "5678"
```

---

## Services & Ports

| Service | External Port | Internal Port | Purpose |
|---------|--------------|---------------|---------|
| StackPilot App | `8080` | `8000` | API + Dashboard + Widget |
| Nginx Proxy Manager | `80`, `443`, `81` | `80`, `443`, `81` | Reverse proxy + SSL + admin |
| n8n | `5678` | `5678` | Workflow automation |
| Ollama | `11434` | `11434` | LLM inference |
| PostgreSQL | internal | `5432` | Database |
| Redis | internal | `6379` | Cache |

---

## Troubleshooting

### App keeps restarting

Check logs:
```bash
docker logs stackpilot-app-1 --tail 50
```

Common issues:
- **Database connection error** — PostgreSQL may still be starting. The app retries automatically for 60 seconds.
- **`invalid DSN`** — Ensure `DATABASE_URL` uses `postgresql://` (not `postgresql+asyncpg://`).

### Widget not loading

- Ensure the `<script>` tag points to the correct URL
- Check browser console for CORS errors
- Verify the app is running: `curl http://YOUR_IP:8080/health`

### Ollama not responding

```bash
docker exec stackpilot-stackpilot-ollama-1 ollama list
```

If no models are listed, pull them via the dashboard or:
```bash
docker exec stackpilot-stackpilot-ollama-1 ollama pull llama3.1
docker exec stackpilot-stackpilot-ollama-1 ollama pull nomic-embed-text
```

### NPM shows 502 Bad Gateway

Ensure the proxy host forward hostname is set to `app` (not `stackpilot-app`).

---

## Project Structure

```
stackpilot/
├── stacker.yml                 # Stacker deployment config
├── .env.example                # Environment template
├── Dockerfile                  # Python backend build
├── requirements.txt            # Python dependencies
├── scripts/
│   ├── generate-secrets.sh     # Secret generation
│   ├── download-model.sh       # Pre-pull Ollama models
│   └── seed-knowledge.sh       # Crawl a URL into KB
└── app/
    ├── main.py                 # FastAPI entry point
    ├── config.py               # Settings from env vars
    ├── database.py             # asyncpg + pgvector setup
    ├── models.py               # Pydantic schemas
    ├── knowledge.py            # KB CRUD, crawling, chunking
    ├── rag.py                  # RAG pipeline, Ollama, n8n
    ├── routes/
    │   ├── widget.py           # Chat API + widget.js
    │   ├── admin.py            # Dashboard, KB management
    │   └── webhooks.py         # n8n + ingestion webhooks
    └── templates/
        └── dashboard.html      # Admin SPA
```

---

## License

MIT
