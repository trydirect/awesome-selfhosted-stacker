# PIPE HOWTO — Connect Two Apps on One Server

Deploy two apps on the same server with `stacker deploy` + `stacker agent
deploy-app`, then connect them with a PIPE. No manual compose editing needed.

## Scenario

Ghost's homepage "Subscribe" form sends a webhook when a visitor signs up.
A PIPE captures that and pushes a notification to UptimeKuma.

**Source:** Ghost (blog) — subscribe form webhook
**Target:** UptimeKuma (monitoring) — push notification receiver

## Step 1: Deploy Ghost

```bash
cd stacker-projects/ghost
./scripts/generate-secrets.sh
stacker config setup server --ip <SERVER_IP> --user root --key ~/.ssh/id_ed25519
stacker deploy --target server --force-rebuild
```

## Step 2: Add UptimeKuma to the same server

```bash
stacker agent deploy-app uptime-kuma --image louislam/uptime-kuma:latest
```

This adds UptimeKuma as a second app on the same server without disturbing
Ghost. Both share the same Docker network so the pipe can connect them.

## Step 3: Create the pipe

```bash
stacker pipe scan --app ghost
stacker pipe scan --app uptime-kuma
stacker pipe create ghost uptime-kuma
```

Map Ghost's subscribe webhook payload to UptimeKuma's push notification
format. Activate the pipe and subscriptions flow through in real time.

## Why this works

| Command | What it does |
|---------|-------------|
| `stacker deploy` | Deploys the project and creates the server deployment |
| `stacker agent deploy-app` | Adds a second app container to the running deployment |
| `stacker pipe create` | Links source and target apps on the same network |
