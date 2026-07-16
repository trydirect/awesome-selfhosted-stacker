# PIPE HOWTO — Ghost Subscribe → Umami Analytics

Deploy Ghost + Umami together on one server with a single `stacker deploy`, then
create a PIPE so every newsletter signup on the Ghost homepage fires a custom
event in Umami.

## What you get

```
Visitor enters email on Ghost homepage "Subscribe" form
  → Ghost fires site.subscription webhook
    → PIPE transforms the payload
      → Umami records "Newsletter Subscribe" event (visible in dashboard)
```

## Step 1: Deploy both apps at once

The `ghost-umami` project bundles both apps and their databases:

```bash
cd stacker-projects/ghost-umami
cp .env.example .env && ./scripts/generate-secrets.sh
# Edit .env: set GHOST_HOST to your domain or IP
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
stacker deploy --target server --force-rebuild
```

This deploys four containers:

| Container | Image | Port |
|-----------|-------|------|
| Ghost (app) | ghost:5-alpine | 2368 |
| Ghost MySQL | mysql:8 | internal |
| Umami | ghcr.io/umami-software/umami:postgresql-latest | 3000 |
| Umami DB | postgres:16-alpine | internal |

## Step 2: Set up the Ghost subscribe webhook

1. Visit `http://<SERVER_IP>:2368/ghost` and create an admin account
2. Go to **Settings → Integrations → Add custom integration**
3. Name it "Subscribe Pipe" and note the **Webhook URL** (used below)

Ghost emits `site.subscription` when anyone uses the homepage "Subscribe" form.

## Step 3: Create the pipe

```bash
stacker pipe scan --app ghost
stacker pipe scan --app umami
```

You should see discoverable endpoints — Ghost's webhook receiver and Umami's
tracking API. Now create the pipe:

```bash
stacker pipe create ghost umami
```

The wizard asks for:

| Prompt | Answer |
|--------|--------|
| Trigger type | `webhook` — fires on Ghost subscribe |
| Source endpoint | Ghost's webhook URL from Step 2 |
| Target endpoint | Umami's `POST /api/send` (custom event endpoint) |
| Field mapping | Transform Ghost subscribe payload to Umami event |

**Field mapping example** — maps the subscriber email from Ghost's webhook
payload to Umami's event format:

```json
{
  "type": "event",
  "payload": {
    "website": "YOUR_UMAMI_WEBSITE_ID",
    "url": "/subscribe",
    "event_type": "Newsletter Subscribe",
    "event_data": {
      "email": "$.subscription.email"
    }
  }
}
```

## Step 4: Activate and test

```bash
stacker pipe activate <pipe-id>
```

The pipe is now live. To test without a real visitor:

```bash
stacker pipe trigger <pipe-id> --data '{"subscription":{"email":"test@example.com"}}'
```

Check the result:

```bash
stacker pipe history <pipe-id>
```

If successful, you'll see the event tracked in Umami at
`http://<SERVER_IP>:3000`.

## How it works

| Component | Role |
|-----------|------|
| Ghost subscribe form | Emits `site.subscription` webhook on signup |
| Stacker PIPE | Captures webhook, transforms payload, routes to target |
| Umami `/api/send` | Receives custom event and records it in analytics |
| Umami dashboard | Shows "Newsletter Subscribe" event in real-time |

## Why this matters

Your marketing team sees subscription signups appear in Umami analytics
instantly — without any custom code, plugins, or third-party services.
