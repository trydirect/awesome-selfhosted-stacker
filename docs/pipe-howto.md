# PIPE HOWTO — Connect Apps with Manual Endpoints

Connect any two apps with a data pipe using manual endpoint specification — no discovery required.

## Quick Start

```bash
stacker pipe create <source> <target> \
  --source-endpoint "METHOD /path" \
  --target-endpoint "METHOD /path" \
  --source-fields field1,field2 \
  --target-fields field1,field2
```

## Example: Directus → Chatwoot

When a new item is created in Directus, send a message to Chatwoot:

```bash
stacker pipe create directus chatwoot \
  --source-endpoint "POST /items" \
  --target-endpoint "POST /api/v1/conversations" \
  --source-fields "name,email,message" \
  --target-fields "content"
```

## How it works

1. **Source endpoint**: Where data comes from (e.g., Directus webhook)
2. **Target endpoint**: Where data goes (e.g., Chatwoot API)
3. **Fields**: Data fields to map between source and target

The pipe automatically maps source fields to target fields using deterministic matching.

## Activation

```bash
stacker pipe list                    # get pipe ID
stacker pipe activate <pipe-id>      # start listening for data
stacker pipe trigger <pipe-id> --data '{"name":"Test","email":"test@example.com","message":"Hello!"}'
stacker pipe history <pipe-id>       # view execution log
```

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
- Run in an interactive terminal, or use `--json` flag for non-interactive output

**Error: "authentication token expired"**
- Run `stacker login` to refresh your session

**Fields not matching**
- Use `--source-fields` and `--target-fields` to explicitly specify field names
