# Chatwoot API Endpoints

## REST API
- Base URL: `http://localhost:3000/api/v1`
- Auth: API access token (Settings → API Access Token)

## Key Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/accounts/{id}/conversations | List conversations |
| POST | /api/v1/accounts/{id}/conversations | Create conversation |
| GET | /api/v1/accounts/{id}/contacts | List contacts |
| POST | /api/v1/accounts/{id}/contacts | Create contact |
| GET | /api/v1/accounts/{id}/agents | List agents |
| GET | /api/v1/accounts/{id}/inboxes | List inboxes |

## Endpoint Specs (for `stacker pipe create`)
| Method | Path | Fields |
|--------|------|--------|
| POST | /api/v1/conversations | content |
| POST | /api/v1/contacts | name,email |
| GET | /api/v1/conversations | — |

## Webhooks
- Configure in Settings → Integrations → Webhooks
- Events: message_created, conversation_created, conversation_updated, etc.

## OpenAPI
- Spec: `http://localhost:3000/swagger_doc`
