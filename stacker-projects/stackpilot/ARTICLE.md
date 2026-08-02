# How to Build a Self-Hosted AI Support Assistant for Your Website (Complete Guide)

**Stop paying $50+/month for AI chat widgets. Deploy your own in 15 minutes — fully self-hosted, no API keys, no vendor lock-in.**

---

## The Problem

Every website needs a support chat. Customers expect instant answers at 2 AM. But the options are grim:

- **Intercom, Drift, Zendesk** — $50-500/month, your data goes to their servers
- **OpenAI-powered widgets** — require API keys, send conversations to OpenAI's servers
- **Generic chatbots** — rigid FAQ trees, no understanding of YOUR content

What if you could run an AI assistant that:
- Lives on your own server
- Learns YOUR website content
- Answers questions using YOUR knowledge base
- Costs nothing after deployment

That's **StackPilot** — a fully self-hosted AI website support assistant.

---

## What StackPilot Does

StackPilot is an open-source stack that combines:

1. **A chat widget** you embed on any website with one `<script>` tag
2. **RAG (Retrieval-Augmented Generation)** that searches your knowledge base for relevant answers
3. **Self-hosted AI** via Ollama — runs Llama 3.1 locally, no API keys needed
4. **Automatic knowledge ingestion** — crawls your website and builds a vector database
5. **Conversation learning** — tracks feedback and improves over time
6. **Workflow automation** — escalates complex issues via n8n

### Architecture

```
Website visitor asks a question
    ↓
Chat widget sends message to StackPilot API
    ↓
Query is embedded into a vector
    ↓
pgvector searches your knowledge base (semantic search)
    ↓
Top relevant documents are injected into the prompt
    ↓
Llama 3.1 generates a response using your content as context
    ↓
Response is returned to the visitor in real-time
    ↓
If the AI is unsure → escalation via n8n webhook
```

---

## Prerequisites

- **Server**: A VPS with 4GB+ RAM (8GB recommended for running LLMs)
- **Docker**: Docker and Docker Compose installed
- **Domain** (optional): For SSL and professional appearance

**Cost comparison:**

| Solution | Monthly Cost | Data Privacy |
|----------|-------------|--------------|
| Intercom | $74-$395/mo | ❌ Their servers |
| Drift | $400+/mo | ❌ Their servers |
| OpenAI Widget | $20-100/mo API | ❌ OpenAI servers |
| **StackPilot** | **$0** (after deploy) | **✅ Your server** |

---

## Step 1: Deploy StackPilot

### Using Stacker (recommended)

```bash
# Clone the repo
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/stackpilot

# Generate secrets
cp .env.example .env
./scripts/generate-secrets.sh

# Deploy to your server
stacker deploy
```

### Using Docker Compose directly

```bash
cd stackpilot
docker compose up -d --build
```

After deployment, you'll have 6 containers running:

| Container | Purpose |
|-----------|---------|
| `stackpilot-app-1` | FastAPI backend (port 8080) |
| `stackpilot-stackpilot-db-1` | PostgreSQL with pgvector |
| `stackpilot-stackpilot-redis-1` | Redis cache |
| `stackpilot-stackpilot-ollama-1` | Ollama LLM inference (port 11434) |
| `stackpilot-stackpilot-n8n-1` | n8n workflow automation (port 5678) |
| `stackpilot-nginx-proxy-manager-1` | Nginx reverse proxy (ports 80/443/81) |

---

## Step 2: Configure the Admin Dashboard

1. Open `http://YOUR_SERVER_IP:8080/api/admin/dashboard`
2. Sign in with the `ADMIN_PASSWORD` from your `.env` file

The dashboard gives you:
- **Overview** — stats on documents, conversations, and resolution rate
- **Knowledge Base** — add, edit, and delete documents
- **Conversations** — view all chat history with feedback
- **Websites** — manage crawled URLs
- **Ollama** — pull and manage AI models

---

## Step 3: Pull AI Models

Go to the **Ollama** tab in the dashboard and pull two models:

1. **`llama3.1`** — the language model that generates responses (~4.9GB)
2. **`nomic-embed-text`** — the embedding model for semantic search (~274MB)

Or via SSH:

```bash
docker exec stackpilot-stackpilot-ollama-1 ollama pull llama3.1
docker exec stackpilot-stackpilot-ollama-1 ollama pull nomic-embed-text
```

**Why these models?**
- **Llama 3.1** is the best open-source model for its size, running well on 8GB RAM
- **nomic-embed-text** produces 768-dimensional embeddings optimized for semantic search

---

## Step 4: Build Your Knowledge Base

### Option A: Auto-crawl your website

1. Go to the **Websites** tab
2. Click **+ Crawl Website**
3. Enter your website URL (e.g., `https://yourcompany.com`)
4. Set max pages (default: 50)
5. Click **Start Crawl**

The crawler will:
- Visit each page on your domain
- Extract text content (stripping HTML, scripts, styles)
- Chunk the text into 500-token pieces
- Embed each chunk using `nomic-embed-text`
- Store embeddings in pgvector

### Option B: Add documents manually

1. Go to the **Knowledge Base** tab
2. Click **+ Add Document**
3. Enter a title, optional source URL, and content
4. Click **Add**

### Option C: Use the ingestion API

```bash
curl -X POST http://YOUR_SERVER:8080/api/webhooks/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Pricing FAQ",
    "content": "Our starter plan costs $29/month and includes...",
    "source": "https://example.com/pricing"
  }'
```

---

## Step 5: Embed the Widget

Add this single line to your website's HTML:

```html
<script src="http://YOUR_SERVER_IP:8080/api/widget/widget.js"></script>
```

That's it. A chat bubble appears in the bottom-right corner of your site.

### Customizing the widget

Edit the `widget.js` endpoint in `app/routes/widget.py` to change:
- Position (`bottom-right` → `bottom-left`)
- Theme colors (`#2563eb` → your brand color)
- Title and subtitle
- Initial welcome message

---

## Step 6: Set Up SSL (Production)

1. Open Nginx Proxy Manager at `http://YOUR_SERVER_IP:81`
2. Log in (check `.env` for credentials or create a new admin)
3. Go to **Proxy Hosts** → **Add Proxy Host**
4. Configure:
   - **Domain**: `support.yourdomain.com`
   - **Forward Hostname**: `app`
   - **Forward Port**: `8000`
   - **Websockets Support**: ON
5. Go to **SSL** tab → **Request a new SSL Certificate**
6. Enable **Force SSL** and **HTTP/2 Support**
7. Save

Update your widget snippet:

```html
<script src="https://support.yourdomain.com/api/widget/widget.js"></script>
```

---

## Step 7: Automate with n8n

StackPilot sends webhook events to n8n when:
- A conversation has low AI confidence (<0.3)
- A visitor seems frustrated

### Setting up an escalation workflow

1. Open n8n at `http://YOUR_SERVER_IP:5678`
2. Create a new workflow
3. Add a **Webhook** trigger at path `/stackpilot`
4. Add actions (e.g., send Slack message, create ticket, email notification)

Example n8n workflow:
```
Webhook → IF confidence < 0.3 → Slack: "Low confidence on: {message}"
```

---

## How the RAG Pipeline Works

### 1. Ingestion Phase

```
Source text → Chunking (500 tokens, 100 overlap)
  → Embedding (nomic-embed-text via Ollama)
  → pgvector storage (768-dim vectors)
```

### 2. Query Phase

```
User question → Embedding → Cosine similarity search (top 5)
  → Context injection → Llama 3.1 generation
  → Response with source references
```

### 3. Learning Phase

```
Conversation stored → Admin marks as "good example"
  → Feeds into fine-tuning pipeline (future)
```

---

## Real-World Use Cases

### SaaS Product Support
- Crawl your docs, API reference, and changelog
- AI answers setup questions, troubleshooting, and billing inquiries
- Escalates technical bugs to engineering via n8n

### E-Commerce Customer Service
- Ingest product catalog, shipping policies, return FAQs
- AI helps with order tracking, product recommendations
- Escalates complaints to human agents

### Internal Knowledge Base
- Deploy behind authentication for team use
- Ingest Notion, Confluence, or Google Docs exports
- AI answers HR questions, processes, and procedures

### Educational Platform
- Crawl course materials and documentation
- AI tutor answers student questions 24/7
- Tracks most-asked questions for content improvement

---

## Performance Tuning

### For low-RAM servers (4GB)

Use smaller models:
```yaml
OLLAMA_MODEL: phi3
OLLAMA_EMBED_MODEL: nomic-embed-text
```

### For better quality (16GB+)

Use larger models:
```yaml
OLLAMA_MODEL: llama3.1:70b
OLLAMA_EMBED_MODEL: nomic-embed-text
```

### For fastest responses

Reduce chunk size and search limit in `app/knowledge.py`:
```python
CHUNK_SIZE = 300  # smaller chunks = faster search
```

---

## Monitoring

### Health check

```bash
curl http://YOUR_SERVER:8080/health
# {"status":"ok","ollama":true}
```

### View logs

```bash
docker logs stackpilot-app-1 -f
docker logs stackpilot-stackpilot-ollama-1 -f
```

### Check stats via API

```bash
curl http://YOUR_SERVER:8080/api/admin/stats
# {"total_documents":142,"total_conversations":38,"resolved_conversations":31,...}
```

---

## FAQ

**Q: How much does it cost to run?**
A: Only your server cost. StackPilot itself is free. A $20/mo VPS handles most workloads.

**Q: Can I use a different LLM?**
A: Yes. Change `OLLAMA_MODEL` in `.env` to any model Ollama supports (Mistral, Gemma, Phi-3, etc.).

**Q: Does it work with Next.js, WordPress, React?**
A: Yes. The widget is a vanilla JS snippet that works with any website technology.

**Q: Can I customize the widget appearance?**
A: Yes. Edit the CSS and HTML in `app/routes/widget.py` in the `serve_widget_js` function.

**Q: How accurate are the answers?**
A: Accuracy depends on your knowledge base quality. The RAG pipeline provides source references so users can verify. Low-confidence answers are automatically escalated.

**Q: Can I use it for multiple websites?**
A: Currently one deployment per website. For multi-tenant use, deploy separate instances or extend the codebase.

---

## Getting Started

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/stackpilot
cp .env.example .env
./scripts/generate-secrets.sh
stacker deploy
```

Then open `http://YOUR_SERVER:8080/api/admin/dashboard` and follow the setup wizard.

---

**StackPilot** is open-source and available at [github.com/trydirect/awesome-selfhosted-stacker](https://github.com/trydirect/awesome-selfhosted-stacker/tree/main/stacker-projects/stackpilot).
