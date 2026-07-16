# PIPE HOWTO — Connect Two Apps on One Server

This guide shows how to deploy two applications on the same server and connect
them with a Stacker PIPE so data flows automatically between them.

## Overview

We'll deploy **Ghost** (blog) and **UptimeKuma** (monitoring) on the same
server and create a pipe so Ghost can push webhook events to UptimeKuma.

**What you'll learn:**

- Deploy two apps on one server via Stacker + manual compose edit
- Scan running containers for discoverable endpoints
- Create and activate a pipe between source and target
- Manually trigger and view execution history

## Prerequisites

- A Linux server with Docker, Docker Compose, and SSH access
- The Stacker CLI installed locally
- A Stacker account (for pipe storage via API)

---

## Step 1: Deploy the first app

Pick any project from `stacker-projects/` and deploy it:

```bash
cd stacker-projects/ghost
./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
stacker deploy --target server --force-rebuild
```

This uploads and runs Ghost (blog) on port 2368 with a MySQL database.

---

## Step 2: Add the second app to the same compose

Stacker deploys one project at a time — each `deploy` overwrites the compose on
the server. To run two apps together, manually add the second app's service
definition to the compose file on the server.

**Download, edit, and re-upload:**

```bash
# Download the current compose from the server
scp root@<SERVER_IP>:/home/trydirect/project/docker-compose.yml .

# Edit it to add the second app (e.g. UptimeKuma)
```

Add the following to the `services:` section (before `networks:`):

```yaml
  uptime-kuma:
    image: louislam/uptime-kuma:latest
    ports:
      - "3001:3001"
    volumes:
      - uptime_kuma_data:/app/data
    restart: unless-stopped
    networks:
      - app-network
```

Add the volume to the `volumes:` section:

```yaml
volumes:
  ghost_content:
  mysql_data:
  uptime_kuma_data:          # <-- add this
```

**Upload the edited compose and start both apps:**

```bash
scp docker-compose.yml root@<SERVER_IP>:/home/trydirect/project/docker-compose.yml
ssh root@<SERVER_IP> "docker compose -f /home/trydirect/project/docker-compose.yml -p project up -d"
```

Verify both are running:

```bash
curl -I http://<SERVER_IP>:2368/   # Ghost
curl -I http://<SERVER_IP>:3001/   # UptimeKuma
```

---

## Step 3: Discover endpoints (pipe scan)

Switch to local mode and scan the running containers:

```bash
stacker target local
stacker pipe scan
```

This discovers API endpoints exposed by the running containers. The output lists
each container's name, exposed ports, and any known endpoint patterns (HTTP,
gRPC, WebSocket, etc.).

---

## Step 4: Create a pipe

Create a pipe between the source app (Ghost) and the target app (UptimeKuma):

```bash
stacker pipe create ghost uptime-kuma
```

This launches an interactive wizard that asks:

- **Trigger type:** `webhook` (fires on HTTP POST), `poll` (checks every N seconds), or `manual`
- **Endpoint mapping:** Which Ghost endpoint emits data, which UptimeKuma endpoint receives it
- **Field mapping:** How to transform data from source format to target format

For Ghost → UptimeKuma:

- Source: Ghost webhook endpoint (`POST /ghost/api/v2/admin/webhooks/`)
- Target: UptimeKuma push endpoint (`POST /api/push/...`)
- Trigger: `webhook` — fires when Ghost publishes a new post
- Field mapping: Map Ghost's `post.current.title` to UptimeKuma's `msg` field

Example mapping:

```json
{
  "msg": "$.post.current.title",
  "status": "up"
}
```

---

## Step 5: Activate the pipe

```bash
stacker pipe activate <pipe-id>
```

The pipe is now live. When Ghost publishes a blog post, it fires a webhook that
Stacker routes to UptimeKuma — the monitoring dashboard shows the new post.

---

## Step 6: Manual trigger & history

Trigger the pipe manually to test:

```bash
stacker pipe trigger <pipe-id> --data '{"post":{"current":{"title":"Hello World"}}}'
```

View execution history:

```bash
stacker pipe history <pipe-id>
```

Re-run a failed execution:

```bash
stacker pipe replay <execution-id>
```

---

## Other app pairs for PIPE

| Source | Target | Use Case |
|--------|--------|----------|
| Ghost (new post webhook) | Telegram / Slack | Notify on blog post |
| WordPress (webhook) | Plausible / Matomo | Track page views in analytics |
| Umami (analytics event) | UptimeKuma (push) | Alert on traffic spikes |
| PostgreSQL (CDC) | Telegram / Webhook | Real-time DB change notifications |
| Contact form | Telegram / Email | Form submission → instant notify |

---

## Known limitations

- **One compose file at a time:** Stacker overwrites the compose on each deploy.
  Adding a second app requires manual compose editing.
- **API dependency:** Pipe creation, activation, and execution history are stored
  via the Stacker API. If the API is unreachable, pipe commands won't work.
- **Local vs remote:** `stacker target local` scans your local Docker daemon.
  For remote servers, use `stacker target server` (requires API + agent).
