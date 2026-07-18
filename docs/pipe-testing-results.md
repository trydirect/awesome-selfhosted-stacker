# PIPE Testing Results

## What we tested

Deployed Directus, Chatwoot, Stirling-PDF, and WordPress on the same server. Ran `stacker pipe scan` and `stacker pipe create` to test endpoint discovery.

## Findings

### Endpoint discovery works — but only for apps with standard patterns

The agent's probe successfully discovers:
- **HTML forms** on pages (found on WordPress with CF7 forms)
- **REST endpoints** at standard paths (`/api`, `/api/v1`, `/api/v2`)

The agent does NOT discover:
- **Directus** REST API at `/items/*` or GraphQL at `/graphql`
- **Chatwoot** REST API at `/api/v1/*`
- **Stirling-PDF** internal API
- **Hanko** REST API at `/v1/*`

### Container resolution works

The agent correctly resolves container names via `my.stacker.service` labels:
```
Container name resolved via compose service label
app_code="project-directus-1" resolved_name="project-directus-1"
```

### Network connectivity works

After connecting the agent to the project network (`docker network connect`), the agent can reach containers on their internal IPs.

### Root cause: agent probe doesn't follow redirects or check specific paths

The agent probes for:
1. OpenAPI/Swagger specs at standard paths (`/api/docs`, `/swagger.json`, etc.)
2. HTML forms on the root page
3. REST API patterns at standard paths

Apps that use non-standard paths (like Directus at `/items/*` or Chatwoot at `/api/v1/*`) are not discovered.

## Workaround

Use apps that expose standard API patterns:
- **WordPress** with Contact Form 7 (forms discovered)
- Apps with OpenAPI specs at standard paths
- Apps with REST APIs at `/api/*` paths

## Next steps

1. Enhance agent probe to check more paths (including app-specific ones documented in `api.md`)
2. Allow manual endpoint specification in `stacker pipe create`
3. Use `api.md` documentation to pre-populate endpoint discovery
