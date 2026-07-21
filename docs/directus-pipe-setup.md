# Connecting Directus to Any Service with Stacker PIPEs

*How to fetch data from Directus and deliver it to any HTTP endpoint — no curl, no scripts, just `stacker pipe`.*

---

## What We Built

A data pipeline that:
1. **Fetches** data from Directus via HTTP (`source_url`)
2. **Transforms** it with JSONPath field mapping
3. **Delivers** it to any HTTP endpoint with auth headers (`target_headers`)

All managed with three CLI commands: `stacker pipe activate`, `stacker pipe trigger`, `stacker pipe list`.

---

## Why We Built It

Every SaaS product eventually faces the same problem: **data trapped in one system needs to reach another**.

Directus holds your content. Chatwoot handles your conversations. Slack gets your notifications. Your CRM tracks your leads. Each has an API. Each needs data from the others.

The traditional approach is scripting: write a bash script with `curl -X POST`, parse JSON with `jq`, handle auth tokens, schedule it with cron, monitor it, fix it when it breaks. Every integration becomes a fragile snowflake that nobody wants to maintain.

We built **PIPEs** to make this composable. Instead of writing a script every time you need to move data between services, you define a pipe once and trigger it with one command:

```bash
stacker pipe trigger <PIPE_ID> --json
```

A PIPE is a reusable data connection. You define the source (where to fetch data), the target (where to send it), and the mapping (how to transform it). Then you activate it on an agent and trigger it whenever you need.

The agent handles the hard parts: HTTP requests across Docker networks, auth headers, JSONPath transformation, error handling, and reporting. You just specify what to connect and let the agent do the plumbing.

Before PIPEs, connecting Directus to Chatwoot meant writing a 50-line bash script with curl, jq, and error handling. Now it's three commands.

---

## Prerequisites

- Stacker CLI installed (`cargo install stacker-cli`)
- A deployed Stacker project with Directus running
- An agent registered and connected to the dashboard

```bash
# Verify agent is connected
stacker agent health --deployment <DEPLOYMENT_HASH>
```

---

## Step 1: Create the Pipe Instance

First, create a pipe instance in the Stacker dashboard. You can do this via the API or UI:

```bash
# Create pipe instance via API
curl -X POST "https://stacker.try.direct/api/v1/pipes/instances" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "name": "directus-to-webhook",
    "source_type": "http",
    "target_type": "http"
  }'
```

Save the returned `pipe_instance_id` — you'll need it for the next steps.

---

## Step 2: Activate the Pipe

Activate the pipe on the agent with your source and target configuration:

```bash
stacker pipe activate <PIPE_INSTANCE_ID> \
  --source-url "http://project-directus-1:8055/items/pages" \
  --trigger manual \
  --target-header "Authorization: Bearer <YOUR_TOKEN>" \
  --deployment <DEPLOYMENT_HASH>
```

This tells the agent:
- **Source**: Fetch from `http://project-directus-1:8055/items/pages`
- **Target**: Deliver to the configured endpoint (set during pipe creation)
- **Headers**: Include `Authorization: Bearer <YOUR_TOKEN>` with every target request
- **Trigger**: Manual only (we'll trigger it explicitly)

Verify the pipe is active:

```bash
stacker pipe list --json --deployment <DEPLOYMENT_HASH>
```

---

## Step 3: Trigger the Pipe

Fetch data from Directus and deliver it:

```bash
stacker pipe trigger <PIPE_INSTANCE_ID> \
  --source-url "http://project-directus-1:8055/items/pages?filter[status][eq]=published" \
  --target-header "Authorization: Bearer <YOUR_TOKEN>" \
  --json \
  --deployment <DEPLOYMENT_HASH>
```

### What Happens

```
┌─────────────────────────────────────────────────────────┐
│  1. AGENT FETCHES SOURCE                                │
│                                                         │
│  GET http://project-directus-1:8055/items/pages         │
│      ?filter[status][eq]=published                      │
│                                                         │
│  Response 200:                                          │
│  {                                                      │
│    "data": [                                            │
│      {"id": 1, "title": "Hello World", "status": "published"},│
│      {"id": 2, "title": "Second Post", "status": "published"} │
│    ]                                                    │
│  }                                                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  2. APPLY FIELD MAPPING (JSONPath)                      │
│                                                         │
│  field_mapping: {"content": "$.data[0].title"}          │
│                                                         │
│  $.data[0].title → "Hello World"                        │
│                                                         │
│  mapped_data = {                                        │
│    "content": "Hello World"                             │
│  }                                                      │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│  3. DELIVER TO TARGET                                   │
│                                                         │
│  POST https://your-webhook-endpoint.com/hook            │
│  Headers:                                               │
│    Authorization: Bearer <YOUR_TOKEN>                   │
│    Content-Type: application/json                       │
│  Body:                                                  │
│    {"content": "Hello World"}                           │
│                                                         │
│  Response 200: OK                                       │
└─────────────────────────────────────────────────────────┘
```

---

## Step 4: Check the Result

View the execution result:

```bash
stacker pipe trigger <PIPE_INSTANCE_ID> \
  --source-url "http://project-directus-1:8055/items/pages" \
  --target-header "Authorization: Bearer <YOUR_TOKEN>" \
  --json \
  --deployment <DEPLOYMENT_HASH>
```

The JSON output includes:

```json
{
  "command_id": "cmd_abc123...",
  "status": "completed",
  "result": {
    "success": true,
    "source_data": {
      "data": [
        {"id": 1, "title": "Hello World", "status": "published"}
      ]
    },
    "mapped_data": {
      "content": "Hello World"
    },
    "target_response": {
      "status": 200,
      "delivered": true,
      "transport": "http"
    }
  }
}
```

---

## Real-World Examples

### Sync Directus Content to Chatwoot

```bash
stacker pipe activate <PIPE_ID> \
  --source-url "http://project-directus-1:8055/items/knowledge_base" \
  --trigger manual \
  --target-header "Authorization: Bearer <CHATWOOT_TOKEN>" \
  --deployment <DEPLOYMENT_HASH>

stacker pipe trigger <PIPE_ID> \
  --source-url "http://project-directus-1:8055/items/knowledge_base?filter[category][eq]=faq" \
  --json \
  --deployment <DEPLOYMENT_HASH>
```

### Send Directus Notifications to Slack

```bash
stacker pipe activate <PIPE_ID> \
  --source-url "http://project-directus-1:8055/items/notifications" \
  --trigger manual \
  --target-header "Authorization: Bearer <SLACK_BOT_TOKEN>" \
  --target-header "Content-Type: application/json" \
  --deployment <DEPLOYMENT_HASH>

stacker pipe trigger <PIPE_ID> \
  --source-url "http://project-directus-1:8055/items/notifications?filter[read][eq]=false" \
  --json \
  --deployment <DEPLOYMENT_HASH>
```

### Push Directus Changes to External API

```bash
stacker pipe activate <PIPE_ID> \
  --source-url "http://project-directus-1:8055/items/products" \
  --trigger manual \
  --target-header "X-API-Key: <YOUR_API_KEY>" \
  --deployment <DEPLOYMENT_HASH>

stacker pipe trigger <PIPE_ID> \
  --source-url "http://project-directus-1:8055/items/products?filter[updated_at][gt]=2026-01-01" \
  --json \
  --deployment <DEPLOYMENT_HASH>
```

---

## Why `source_url`?

Before `source_url`, pipes required `source_container` — the agent had to be on the same Docker network as the source service. This meant:

- Complex network configuration
- Agent couldn't reach external services
- No support for authenticated APIs

With `source_url`:
- Agent fetches any HTTP endpoint directly
- Works across Docker networks
- Supports `target_headers` for auth
- No curl needed — everything through `stacker pipe`

---

## Troubleshooting

### "source fetch failed with status 403"

Directus requires authentication. Add the admin token to the source URL or configure Directus to allow public read access:

```bash
# Option 1: Add token to source URL (if Directus supports query param auth)
stacker pipe trigger <PIPE_ID> \
  --source-url "http://directus:8055/items/pages?access_token=<TOKEN>" \
  --json

# Option 2: Configure Directus public role permissions
```

### "target request failed with status 404"

The target endpoint doesn't exist. Check the API path:

```bash
# Wrong
--target-url "http://chatwoot:3000/api/v1/conversations"

# Correct (Chatwoot example)
--target-url "http://chatwoot:3000/api/v1/accounts/<ACCOUNT_ID>/conversations"
```

### "pipe_instance_id is not active on this agent"

Activate the pipe first:

```bash
stacker pipe activate <PIPE_ID> --trigger manual --deployment <DEPLOYMENT_HASH>
```

---

## Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Directus   │     │  Stacker     │     │   Target     │
│              │     │  Agent       │     │   Service    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │  HTTP GET          │                    │
       │◄───────────────────│                    │
       │  (source_url)      │                    │
       │                    │  field_mapping     │
       │                    │  (JSONPath)        │
       │                    │                    │
       │                    │  HTTP POST         │
       │                    │  (target_headers)  │
       │                    │───────────────────►│
       │                    │                    │
```

---

## Summary

With three commands, you can build data pipelines between Directus and any HTTP service:

```bash
# 1. Activate
stacker pipe activate <PIPE_ID> \
  --source-url "http://directus:8055/items/<COLLECTION>" \
  --trigger manual \
  --target-header "Authorization: Bearer <TOKEN>"

# 2. Trigger
stacker pipe trigger <PIPE_ID> \
  --json

# 3. List pipes
stacker pipe list --json
```

No curl. No scripts. Just `stacker pipe`.

---

*Built with Stacker v0.3.1 — [https://stacker.dev](https://stacker.dev)*
