# Gotify

**Self-hosted push notification server** — simple server for sending and receiving push notifications.

## Deploy with Stacker

```bash
git clone https://github.com/trydirect/awesome-selfhosted-stacker.git
cd awesome-selfhosted-stacker/stacker-projects/gotify

# Deploy
stacker deploy --target cloud --key htz-0
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| Gotify | 8080 | Notification server UI |
