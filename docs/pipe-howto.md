# PIPE HOWTO — Connect Apps with Manual Endpoints

Connect any two apps with a data pipe using manual endpoint specification — no discovery required.

## Quick Start

```bash
stacker pipe create <source> <target> \
  --source-endpoint "METHOD /path" \
  --target-endpoint "METHOD /path" \
  --source-fields field1,field2 \
  --target-fields field1,field2 \
  --name "my-pipe"
```

## Example: Directus → Chatwoot

When a new item is created in Directus, send a message to Chatwoot:

```bash
stacker pipe create directus chatwoot \
  --source-endpoint "POST /items" \
  --target-endpoint "POST /api/v1/conversations" \
  --source-fields "name,email,message" \
  --target-fields "content" \
  --name "directus-chatwoot"
```

## Example: apprise → ntfy (webhook, end-to-end verified)

apprise has no auto-discoverable API, so it can only be piped with manual
endpoints. Deliver a payload to ntfy's `POST /{topic}` webhook:

```bash
stacker pipe create app ntfy \
  --source-endpoint "GET /status" \
  --target-endpoint "POST /pipetest" \
  --source-fields message \
  --target-fields message \
  --name apprise-to-ntfy

stacker pipe activate <pipe-id> --trigger manual
stacker pipe trigger  <pipe-id> --data '{"message":"hello from the pipe"}'   # → delivered: true

# verify the target received it:
curl "http://<server-ip>:8080/pipetest/json?poll=1"
# {"event":"message","topic":"pipetest","message":"{\"message\":\"hello from the pipe\"}"}
```

(Both apps must be co-located on one server so the agent can resolve each
container by its `my.stacker.service` label.)

## How it works

1. **Source endpoint**: Where data comes from (e.g., Directus webhook)
2. **Target endpoint**: Where data goes (e.g., Chatwoot API)
3. **Fields**: Data fields to map between source and target
4. **Name**: Pipe name (skips interactive prompt)

Fields are mapped source → target by matching field **name**, falling back to
**positional** alignment, then **identity** (`target ← $.target`). An empty
`--target-fields` produces a pass-through mapping (the whole payload).

When both `--source-endpoint` and `--target-endpoint` are given, endpoint
**discovery is skipped entirely** — so this works for apps whose APIs aren't
auto-discoverable (and is fully non-interactive/scriptable).

## Activation

```bash
stacker pipe list                                 # get the pipe instance ID
stacker pipe activate <pipe-id> --trigger manual  # arm for manual triggering
stacker pipe trigger <pipe-id> --data '{"name":"Test","email":"test@example.com","message":"Hello!"}'
stacker pipe history <pipe-id>                     # view execution log (✓ success)
```

> Use `--trigger manual` so the pipe fires on `pipe trigger`. `--trigger webhook`
> (the default) and `--trigger poll --poll-interval <s>` are also available.

## Benefits

- **No discovery required**: Works even when apps aren't running
- **No agent dependency**: Bypasses endpoint discovery limitations
- **Immediate**: Create pipes in seconds
- **Flexible**: Works with any HTTP API endpoint

## Supported endpoint formats

| Format | Example |
|--------|---------|
| Method + path | `POST /api/v1/items` |
| Bare path (defaults to GET) | `/api/v1/items` |

## Troubleshooting

**Error: "not a terminal"**
- Use `--name` flag to skip interactive prompts

**Error: "authentication token expired"**
- Run `stacker login` to refresh your session

**Fields not matching**
- Use `--source-fields` and `--target-fields` to explicitly specify field names
