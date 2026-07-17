# How To: Connect Supabase and PostHog with a Stacker Pipe

Create a working data pipe between a Supabase stack (Kong + PostgREST) and a PostHog-compatible event receiver using Stacker.

---

## Prerequisites

- Stacker CLI installed and authenticated (`stacker login`)
- Hetzner cloud credentials configured (`stacker clouds`)
- Docker running locally (for image transfer if needed)

---

## Step 1 — Create the project

```bash
stacker init supabase-posthog
```

Set the project identity in `stacker.yml`:

```yaml
name: supabase-posthog
project:
  identity: supabase-posthog
```

## Step 2 — Define the stack

Configure the application and services in `stacker.yml`. The main app is Kong, acting as the API gateway. Add Supabase services (db, auth, rest, realtime, storage, meta, studio) and a PostHog-compatible event receiver.

**Key config:**

```yaml
app:
  type: custom
  image: kong/kong:3.9.1
  ports:
    - "8000:8000"
    - "8443:8443"

services:
  - name: db
    image: supabase/postgres:17.6.1.136
    # ... database init, healthcheck, volumes

  - name: posthog
    image: python:3.11-alpine
    ports:
      - "8001:8000"
    volumes:
      - ./posthog-receiver/app.py:/app/app.py:ro
    command: python /app/app.py
```

### Kong route configuration

Create `kong.yml` with upstream timeouts to avoid probe hangs:

```yaml
services:
  - name: rest-v1
    url: http://rest:3000
    connect_timeout: 5000
    write_timeout: 5000
    read_timeout: 5000
    routes:
      - name: rest-all
        paths:
          - /rest/v1/

  - name: posthog-v1
    url: http://posthog:8000
    connect_timeout: 5000
    write_timeout: 5000
    read_timeout: 5000
    routes:
      - name: posthog-capture
        paths:
          - /posthog/
```

Without explicit timeouts, Kong defaults to 60s per upstream operation. Probes that hit a down service would hang for the full duration.

## Step 3 — Deploy to cloud

```bash
stacker deploy --target cloud --key htz-0
```

This provisions a Hetzner server, installs Docker and the status panel agent, copies the config bundle, and starts all containers.

After deployment completes, verify:

```bash
stacker status
stacker agent status
stacker agent containers
```

All services should show `running`. If some are `restarting`, check their logs:

```bash
stacker agent logs rest --limit 20   # rest - is the container name
```

## Step 4 — Create the pipe

The pipe connects a source endpoint (Supabase PostgREST) to a target endpoint (PostHog `/capture`).

First, scan the running apps to discover endpoints — note that the probe takes 3-5 minutes, so the CLI timeout may need extending:

```bash
# Using pipe scan (may time out if probe takes long)
stacker pipe scan --app supabase-posthog

# Alternative: use agent exec with a longer timeout
stacker agent exec probe_endpoints \
  --params '{"app_code":"supabase-posthog","capture_samples":true}' \
  --timeout 600 --json
```

Then create the pipe:

```bash
stacker pipe create supabase-posthog posthog --manual
```

## Step 5 — Test the pipe

Verify the PostHog receiver accepts events:

```bash
# Direct to PostHog
curl -X POST http://<SERVER_IP>:8001/capture \
  -H "Content-Type: application/json" \
  -d '{"event":"test","properties":{"source":"pipe-demo"}}'

# Through Kong
curl -X POST http://<SERVER_IP>:8000/posthog/capture \
  -H "Content-Type: application/json" \
  -d '{"event":"test","properties":{"source":"pipe-demo"}}'
```

Check the PostHog logs to confirm receipt:

```bash
stacker agent logs posthog --limit 10
```

Expected output:

```
Received capture event: {"event": "test", "properties": {"source": "pipe-demo"}}
```

---

## Troubleshooting

### Probe hangs or times out

**Symptom:** `pipe scan` or `pipe create` reports "timed out"

**Most common cause:** The remote `docker-compose.yml` is invalid — missing volume definitions, undefined networks, or file ownership issues. Run `docker compose ps` on the server to check:

```bash
ssh trydirect@<SERVER_IP>
cd /home/trydirect/project
docker compose ps
```

If it errors with "refers to undefined network" or "refers to undefined volume", the compose file is broken. Check that `networks:` and `volumes:` sections match what services reference.

**Validator:**
```bash
docker compose config
```

### Probe works but endpoints are empty

**Symptom:** Probe completes but returns `"endpoints": []`

**Check:** Kong upstream timeouts. If Kong's upstream connections hang (default 60s), the probe waits for each timeout. Set `connect_timeout`, `write_timeout`, `read_timeout` to 5000ms on all Kong services.

### Container name not resolved

**Symptom:** Agent logs show `"Failed to inspect"` or containers list is empty

**Check:** The agent needs access to Docker and a valid compose file. Run `docker compose ps` directly on the server. If it fails, fix the compose file first.

### Agent responds slowly

**Symptom:** Agent commands take minutes to execute

**Check:** If the compose file is invalid, every agent operation (`list_containers`, `deploy_app`, etc.) that validates the compose will hang. Fix the compose file first, then restart the agent:

```bash
ssh trydirect@<SERVER_IP>
sudo docker compose -f /home/trydirect/statuspanel/docker-compose.yml up -d
```

---

## Verification checklist

- [ ] `stacker deployments` shows all deployments 
- [ ] `stacker status` shows last deployment status
- [ ] `stacker agent containers` lists all services as `running`
- [ ] `stacker agent exec probe_endpoints` returns endpoints with operations
- [ ] Direct curl to PostHog `/capture` returns `{"status": "ok"}`
- [ ] Events appear in `stacker agent logs posthog`

---
