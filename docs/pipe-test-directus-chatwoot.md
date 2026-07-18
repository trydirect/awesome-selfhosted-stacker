# Directus → Chatwoot PIPE Test

## Deploy both apps

```bash
# Combined compose with Directus + Chatwoot
docker compose -f docker-compose.yml -p project up -d
```

## PIPE workflow (when agent is configured)

```bash
# 1. Scan both apps for endpoints
stacker pipe scan --app directus --container project-directus-1
stacker pipe scan --app chatwoot --container project-chatwoot-1

# 2. Create pipe
stacker pipe create directus chatwoot

# 3. Activate
stacker pipe activate <pipe-id>

# 4. Test
stacker pipe trigger <pipe-id> --data '{"event":"item.created","collection":"posts"}'
```

## Known issues

- `remote_app` scope returns empty (agent doesn't pass resolved containers to probe)
- `direct_container` scope works (use `--container` flag)
- Agent must be on same Docker network as project containers
- CLI auth token expires — need `stacker login` before pipe commands

## Expected flow

```
Directus data change → webhook → PIPE → Chatwoot incoming message
```
