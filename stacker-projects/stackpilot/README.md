# StackPilot

Self-hosted AI website support assistant powered by Ollama, pgvector, and n8n.

## What it does

- Embeds an AI chat widget on any website
- Answers questions using RAG (Retrieval-Augmented Generation) over your knowledge base
- Crawls your website to automatically build the knowledge base
- Learns from conversations (feedback loop)
- Escalates complex issues to n8n for ticket creation / notifications
- Fully self-hosted — no external AI APIs needed

## Stack

| Service | Image | Purpose |
|---------|-------|---------|
| app | Custom Python (FastAPI) | API, RAG pipeline, admin dashboard, widget |
| stackpilot-db | pgvector/pgvector:0.8.0-pg16 | Knowledge base vectors + conversation history |
| stackpilot-redis | redis:7-alpine | Caching, rate limiting |
| stackpilot-ollama | ollama/ollama:latest | Self-hosted LLM inference + embeddings |
| stackpilot-n8n | n8nio/n8n:latest | Workflow automation, escalation |

## Quick Start

```bash
cp .env.example .env
./scripts/generate-secrets.sh
stacker deploy
```

## First Run

1. Open the dashboard: `http://localhost:8080/api/admin/dashboard`
2. Sign in with the `ADMIN_PASSWORD` from your `.env`
3. Go to **Ollama** tab and pull the default models (llama3.1 + nomic-embed-text)
4. Go to **Websites** tab and crawl your website URL
5. Add the widget snippet to your website

## Widget Snippet

Add this to your website's HTML:

```html
<script src="http://localhost:8080/api/widget/widget.js"></script>
```

Replace `localhost:8080` with your actual StackPilot URL.

## API Endpoints

### Widget
- `POST /api/widget/chat` — Send a message, get an AI response
- `GET /api/widget/widget.js` — Embeddable chat widget script

### Admin
- `GET /api/admin/stats` — Dashboard statistics
- `GET /api/admin/documents` — List knowledge base documents
- `POST /api/admin/documents` — Add a document
- `DELETE /api/admin/documents/{id}` — Remove a document
- `POST /api/admin/websites/crawl` — Crawl a website
- `GET /api/admin/conversations` — List conversations
- `GET /api/admin/ollama/status` — Check Ollama health
- `POST /api/admin/ollama/pull` — Pull a model

### Webhooks
- `POST /api/webhooks/n8n` — n8n callback endpoint
- `POST /api/webhooks/ingest` — External content ingestion

## Data Flow

```
Website → widget.js → /api/widget/chat
  → embed query → pgvector search (top-K)
  → build context → Ollama generate
  → return response
  → store conversation
  → if low confidence → escalate via n8n
```

## Configuration

All config via environment variables (`.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | — | Session signing key |
| DB_PASSWORD | — | Postgres password |
| ADMIN_PASSWORD | — | Dashboard login |
| N8N_PASSWORD | — | n8n basic auth |
| OLLAMA_MODEL | llama3.1 | LLM model for responses |
| OLLAMA_EMBED_MODEL | nomic-embed-text | Embedding model |
